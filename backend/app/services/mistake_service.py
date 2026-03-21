from sqlalchemy.orm import Session

from app.models.mistake_record import MistakeRecord
from app.models.task_record import TaskRecord
from app.schemas.chat import MistakeItemResponse, MistakeListResponse, QuizAttemptRequest, QuizAttemptResponse


class MistakeService:
    def submit_quiz_attempt(self, db: Session, user_id: int, record: TaskRecord, payload: QuizAttemptRequest) -> QuizAttemptResponse:
        quiz_items = (record.result_json or {}).get("quiz") or []
        answers_map = {item.questionIndex: item.userAnswer.upper().strip() for item in payload.answers}

        correct_count = 0
        saved_mistakes = 0
        for index, quiz_item in enumerate(quiz_items):
            correct_answer = str(quiz_item.get("answer", "")).upper().strip()
            user_answer = answers_map.get(index, "")
            if user_answer == correct_answer:
                correct_count += 1
                continue
            if not user_answer:
                continue

            db.add(
                MistakeRecord(
                    user_id=user_id,
                    session_id=record.session_id or "",
                    task_record_id=record.id,
                    question=str(quiz_item.get("question", "")).strip(),
                    options_json=list(quiz_item.get("options", [])),
                    correct_answer=correct_answer,
                    user_answer=user_answer,
                    source_excerpt=self._first_source_excerpt(record),
                )
            )
            saved_mistakes += 1

        db.commit()

        total_questions = len(quiz_items)
        return QuizAttemptResponse(
            savedMistakes=saved_mistakes,
            totalQuestions=total_questions,
            correctCount=correct_count,
            message=f"已记录 {saved_mistakes} 道错题，答对 {correct_count}/{total_questions}。",
        )

    def list_mistakes(self, db: Session, user_id: int, limit: int = 20) -> MistakeListResponse:
        rows = (
            db.query(MistakeRecord)
            .filter(MistakeRecord.user_id == user_id)
            .order_by(MistakeRecord.created_at.desc(), MistakeRecord.id.desc())
            .limit(limit)
            .all()
        )

        return MistakeListResponse(
            items=[
                MistakeItemResponse(
                    id=row.id,
                    sessionId=row.session_id,
                    taskRecordId=row.task_record_id,
                    question=row.question,
                    options=list(row.options_json or []),
                    correctAnswer=row.correct_answer,
                    userAnswer=row.user_answer,
                    sourceExcerpt=row.source_excerpt,
                    createdAt=row.created_at,
                )
                for row in rows
            ]
        )

    def _first_source_excerpt(self, record: TaskRecord) -> str | None:
        chunks = record.retrieved_chunks_json or []
        if not chunks:
            return None
        content = str(chunks[0].get("content", "")).strip()
        if len(content) > 120:
            return f"{content[:120]}..."
        return content or None
