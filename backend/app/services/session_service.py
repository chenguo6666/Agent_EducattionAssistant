import uuid
from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.chat_session import ChatSession


class SessionService:
    def get_owned_session(self, db: Session, user_id: int, session_id: str) -> ChatSession:
        session = (
            db.query(ChatSession)
            .filter(ChatSession.id == session_id, ChatSession.user_id == user_id)
            .first()
        )
        if session is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="会话不存在")
        return session

    def get_or_create_session(
        self,
        db: Session,
        user_id: int,
        session_id: str | None,
        title_seed: str,
        title_prefix: str = "",
    ) -> ChatSession:
        if session_id:
            return self.get_owned_session(db=db, user_id=user_id, session_id=session_id)

        title = self.build_session_title(title_seed, prefix=title_prefix)
        session = ChatSession(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=title,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        db.add(session)
        db.flush()
        return session

    def touch_session(self, db: Session, session: ChatSession) -> None:
        session.updated_at = datetime.utcnow()
        db.add(session)

    def build_session_title(self, source: str, prefix: str = "") -> str:
        normalized = " ".join(source.strip().split())
        if prefix:
            normalized = f"{prefix}{normalized}"
        if len(normalized) <= 24:
            return normalized
        return f"{normalized[:24]}..."
