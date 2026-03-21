from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentSummaryResponse
from app.services.document_service import DocumentService

router = APIRouter(prefix="/api/documents", tags=["documents"])
service = DocumentService()


@router.post("/upload", response_model=DocumentSummaryResponse)
async def upload_document(
    file: UploadFile = File(...),
    sessionId: str | None = Form(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return await service.upload(db=db, user_id=current_user.id, file=file, session_id=sessionId)


@router.get("/sessions/{session_id}", response_model=DocumentListResponse)
def list_session_documents(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_session_documents(db=db, user_id=current_user.id, session_id=session_id)
