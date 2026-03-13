import uuid

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.agent.orchestrator import AgentOrchestrator
from app.models.chat_session import ChatSession
from app.models.task_record import TaskRecord
from app.schemas.chat import (
    AgentTraceItem,
    ChatResponse,
    ChatResult,
    ChatSessionDetailResponse,
    ChatSessionListResponse,
    ChatSessionSummary,
    TaskRecordResponse,
    TaskStage,
    ToolCallItem,
)
from app.schemas.document import RetrievedChunkResponse
from app.services.document_service import DocumentService
from app.services.session_service import SessionService


class ChatService:
    def __init__(self) -> None:
        self.session_service = SessionService()
        self.document_service = DocumentService()
        self.orchestrator = AgentOrchestrator()

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
        recent_messages = self._get_recent_messages(db=db, session_id=session.id)

        execution = self.orchestrator.run(
            db=db,
            user_id=user_id,
            session_id=session.id,
            message=message,
            material_text=material_text,
            used_documents=used_documents,
            recent_messages=recent_messages,
        )

        record = TaskRecord(
            session_id=session.id,
            user_id=user_id,
            message=message,
            intent=execution.intent,
            status=execution.status,
            steps_json=execution.steps,
            timeline_json=[stage.model_dump() for stage in execution.timeline],
            result_json=execution.result.model_dump(exclude_none=True),
            agent_trace_json=[item.model_dump() for item in execution.agent_trace],
            tool_calls_json=[item.model_dump() for item in execution.tool_calls],
            retrieved_chunks_json=[chunk.model_dump() for chunk in execution.retrieved_chunks],
            error_message=None if execution.status != "failed" else "任务执行失败",
        )
        db.add(record)
        db.flush()

        response = ChatResponse(
            taskId=f"task_{uuid.uuid4().hex[:8]}",
            recordId=record.id,
            sessionId=session.id,
            intent=execution.intent,
            status=execution.status,
            steps=execution.steps,
            timeline=execution.timeline,
            result=execution.result,
            agentTrace=execution.agent_trace,
            toolCalls=execution.tool_calls,
            usedDocuments=used_documents,
            retrievedChunks=execution.retrieved_chunks,
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
        agent_trace = [AgentTraceItem(**item) for item in (record.agent_trace_json or [])]
        tool_calls = [ToolCallItem(**item) for item in (record.tool_calls_json or [])]
        return TaskRecordResponse(
            id=record.id,
            message=record.message,
            intent=record.intent,
            status=record.status,
            steps=list(record.steps_json or []),
            timeline=timeline,
            result=ChatResult(**(record.result_json or {})),
            agentTrace=agent_trace,
            toolCalls=tool_calls,
            retrievedChunks=retrieved_chunks,
            errorMessage=record.error_message,
            createdAt=record.created_at,
        )

    def _get_recent_messages(self, db: Session, session_id: str) -> list[str]:
        rows = (
            db.query(TaskRecord.message)
            .filter(TaskRecord.session_id == session_id)
            .order_by(TaskRecord.created_at.desc(), TaskRecord.id.desc())
            .limit(6)
            .all()
        )
        return [row[0] for row in reversed(rows)]
