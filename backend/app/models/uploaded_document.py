from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False, index=True)
    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(20), nullable=False)
    content_type: Mapped[str] = mapped_column(String(120), nullable=False, default="application/octet-stream")
    file_size: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    extracted_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    extraction_status: Mapped[str] = mapped_column(String(20), nullable=False, default="completed")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
