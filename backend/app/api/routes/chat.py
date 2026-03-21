from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatSessionDetailResponse,
    ChatSessionListResponse,
    ExportResponse,
    MistakeListResponse,
    QuizAttemptRequest,
    QuizAttemptResponse,
)
from app.services.chat_service import ChatService
from app.services.export_service import ExportService
from app.services.mistake_service import MistakeService

router = APIRouter(prefix="/api/chat", tags=["chat"])
service = ChatService()
export_service = ExportService()
mistake_service = MistakeService()


@router.post("/execute", response_model=ChatResponse)
def execute_task(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.execute(db=db, user_id=current_user.id, message=payload.message, session_id=payload.sessionId)


@router.get("/sessions", response_model=ChatSessionListResponse)
def list_sessions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_sessions(db=db, user_id=current_user.id)


@router.get("/sessions/{session_id}", response_model=ChatSessionDetailResponse)
def get_session_detail(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_session_detail(db=db, user_id=current_user.id, session_id=session_id)


@router.get("/records/{record_id}/export", response_model=ExportResponse)
def export_task_result(record_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    record = service.get_owned_record(db=db, user_id=current_user.id, record_id=record_id)
    return export_service.export_task_markdown(record)


@router.post("/records/{record_id}/quiz-attempt", response_model=QuizAttemptResponse)
def submit_quiz_attempt(
    record_id: int,
    payload: QuizAttemptRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    record = service.get_owned_record(db=db, user_id=current_user.id, record_id=record_id)
    return mistake_service.submit_quiz_attempt(db=db, user_id=current_user.id, record=record, payload=payload)


@router.get("/mistakes", response_model=MistakeListResponse)
def list_mistakes(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return mistake_service.list_mistakes(db=db, user_id=current_user.id)
