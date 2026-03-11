from fastapi import APIRouter, Depends

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.chat_service import ChatService

router = APIRouter(prefix="/api/chat", tags=["chat"])
service = ChatService()


@router.post("/execute", response_model=ChatResponse)
def execute_task(payload: ChatRequest, current_user: User = Depends(get_current_user)):
    return service.execute(payload.message)
