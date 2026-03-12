import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agent.planner import TaskPlanner
from app.models.chat_session import ChatSession
from app.models.task_record import TaskRecord
from app.schemas.chat import (
    ChatResponse,
    ChatResult,
    ChatSessionDetailResponse,
    ChatSessionListResponse,
    ChatSessionSummary,
    TaskRecordResponse,
    TaskStage,
)
from app.schemas.document import RetrievedChunkResponse
from app.services.document_service import DocumentService
from app.services.gemini_service import GeminiService
from app.services.retrieval_service import RetrievalService
from app.services.session_service import SessionService
from app.services.status import STATUS_ANALYZING, STATUS_COMPLETED, STATUS_EXECUTING, STATUS_SUBMITTED
from app.tools.quiz_tool import generate_quiz
from app.tools.summary_tool import summarize_text


class ChatService:
    def __init__(self) -> None:
        self.planner = TaskPlanner()
        self.session_service = SessionService()
        self.document_service = DocumentService()
        self.gemini_service = GeminiService()
        self.retrieval_service = RetrievalService()

    def execute(self, db: Session, user_id: int, message: str, session_id: str | None = None) -> ChatResponse:
        session = self.session_service.get_or_create_session(
            db=db,
            user_id=user_id,
            session_id=session_id,
            title_seed=message,
        )
        material_text, used_documents = self.document_service.get_session_material_text(
            db=db,
            user_id=user_id,
            session_id=session.id,
        )
        plan = self.planner.plan(message, has_material=bool(used_documents))
        recent_messages = self._get_recent_messages(db=db, session_id=session.id)
        retrieval_query = self.retrieval_service.maybe_enrich_query(message, recent_messages)
        retrieved_chunks = (
            self.retrieval_service.retrieve(db=db, user_id=user_id, session_id=session.id, query=retrieval_query, top_k=4)
            if used_documents
            else []
        )
        retrieved_context = self.retrieval_service.build_context_text(retrieved_chunks)
        source_text = retrieved_context or material_text or message
        summary = None
        quiz = None
        answer = None
        steps = list(plan.steps)

        if used_documents:
            steps.insert(1, f"读取会话资料：{len(used_documents)} 个文件")
        if retrieved_chunks:
            steps.insert(2, f"检索到相关片段：{len(retrieved_chunks)} 条")

        if plan.intent in {"summary", "summary_and_quiz", "unknown"}:
            summary = self.gemini_service.summarize(task=message, material=source_text) or summarize_text(source_text)

        if plan.intent in {"quiz", "summary_and_quiz"}:
            quiz_count = 5 if "5" in message else 3
            quiz = self.gemini_service.generate_quiz(task=message, material=source_text, count=quiz_count) or generate_quiz(source_text, count=quiz_count)

        if plan.intent == "rag_answer":
            answer = self.gemini_service.answer_question(question=retrieval_query, context=source_text) or self._build_local_answer(retrieved_chunks)

        timeline = [
            TaskStage(status=STATUS_SUBMITTED, label="任务已提交"),
            TaskStage(status=STATUS_ANALYZING, label="正在分析任务意图"),
            TaskStage(status=STATUS_EXECUTING, label="正在调用工具"),
            TaskStage(status=STATUS_COMPLETED, label="任务执行完成"),
        ]

        record = TaskRecord(
            session_id=session.id,
            user_id=user_id,
            message=message,
            intent=plan.intent,
            status=STATUS_COMPLETED,
            steps_json=steps,
            timeline_json=[stage.model_dump() for stage in timeline],
            result_json=ChatResult(summary=summary, quiz=quiz, answer=answer).model_dump(exclude_none=True),
            retrieved_chunks_json=[chunk.model_dump() for chunk in retrieved_chunks],
            error_message=None,
        )
        db.add(record)
        db.flush()

        response = ChatResponse(
            taskId=f"task_{uuid.uuid4().hex[:8]}",
            recordId=record.id,
            sessionId=session.id,
            intent=plan.intent,
            status=STATUS_COMPLETED,
            steps=steps,
            timeline=timeline,
            result=ChatResult(summary=summary, quiz=quiz, answer=answer),
            usedDocuments=used_documents,
            retrievedChunks=retrieved_chunks,
        )

        self.session_service.touch_session(db=db, session=session)
        db.commit()

        return response

    def list_sessions(self, db: Session, user_id: int) -> ChatSessionListResponse:
        sessions = (
            db.query(ChatSession)
            .filter(ChatSession.user_id == user_id)
            .order_by(ChatSession.updated_at.desc(), ChatSession.created_at.desc())
            .all()
        )

        summaries: list[ChatSessionSummary] = []
        for session in sessions:
            latest_record = (
                db.query(TaskRecord)
                .filter(TaskRecord.session_id == session.id)
                .order_by(TaskRecord.created_at.desc(), TaskRecord.id.desc())
                .first()
            )
            summaries.append(
                ChatSessionSummary(
                    sessionId=session.id,
                    title=session.title,
                    lastMessage=latest_record.message if latest_record else "",
                    lastStatus=latest_record.status if latest_record else None,
                    createdAt=session.created_at,
                    updatedAt=session.updated_at,
                )
            )

        return ChatSessionListResponse(sessions=summaries)

    def get_session_detail(self, db: Session, user_id: int, session_id: str) -> ChatSessionDetailResponse:
        session = self.session_service.get_owned_session(db=db, user_id=user_id, session_id=session_id)
        records = (
            db.query(TaskRecord)
            .filter(TaskRecord.session_id == session.id)
            .order_by(TaskRecord.created_at.asc(), TaskRecord.id.asc())
            .all()
        )
        documents = self.document_service.list_session_documents(db=db, user_id=user_id, session_id=session.id)

        return ChatSessionDetailResponse(
            sessionId=session.id,
            title=session.title,
            createdAt=session.created_at,
            updatedAt=session.updated_at,
            tasks=[self._serialize_task_record(record) for record in records],
            documents=documents.documents,
        )

    def get_owned_record(self, db: Session, user_id: int, record_id: int) -> TaskRecord:
        record = db.query(TaskRecord).filter(TaskRecord.id == record_id, TaskRecord.user_id == user_id).first()
        if record is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="任务记录不存在")
        return record

    def _serialize_task_record(self, record: TaskRecord) -> TaskRecordResponse:
        timeline = [TaskStage(**item) for item in (record.timeline_json or [])]
        retrieved_chunks = [RetrievedChunkResponse(**item) for item in (record.retrieved_chunks_json or [])]
        return TaskRecordResponse(
            id=record.id,
            message=record.message,
            intent=record.intent,
            status=record.status,
            steps=list(record.steps_json or []),
            timeline=timeline,
            result=ChatResult(**(record.result_json or {})),
            retrievedChunks=retrieved_chunks,
            errorMessage=record.error_message,
            createdAt=record.created_at,
        )

    def _get_recent_messages(self, db: Session, session_id: str) -> list[str]:
        rows = (
            db.query(TaskRecord.message)
            .filter(TaskRecord.session_id == session_id)
            .order_by(TaskRecord.created_at.desc(), TaskRecord.id.desc())
            .limit(2)
            .all()
        )
        return [row[0] for row in reversed(rows)]

    def _build_local_answer(self, retrieved_chunks: list[RetrievedChunkResponse]) -> str:
        if not retrieved_chunks:
            return "当前资料中没有检索到足够相关的片段，请尝试换一种问法或补充更明确的关键词。"

        bullet_lines = []
        for chunk in retrieved_chunks[:3]:
            excerpt = chunk.content
            if len(excerpt) > 120:
                excerpt = f"{excerpt[:120]}..."
            bullet_lines.append(f"- 来源《{chunk.fileName}》：{excerpt}")

        return "根据检索到的资料片段，可以参考以下内容：\n" + "\n".join(bullet_lines)
