from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MistakeRecord(Base):
    __tablename__ = "mistake_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False, index=True)
    task_record_id: Mapped[int] = mapped_column(ForeignKey("task_records.id"), nullable=False, index=True)
    question: Mapped[str] = mapped_column(Text, nullable=False)
    options_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    correct_answer: Mapped[str] = mapped_column(String(4), nullable=False)
    user_answer: Mapped[str] = mapped_column(String(4), nullable=False)
    source_excerpt: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
