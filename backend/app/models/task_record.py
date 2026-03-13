from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime

from app.core.database import Base


class TaskRecord(Base):
    __tablename__ = "task_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[str | None] = mapped_column(ForeignKey("chat_sessions.id"), nullable=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    intent: Mapped[str] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    steps_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    timeline_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    result_json: Mapped[dict] = mapped_column(JSON, nullable=False, default=dict)
    agent_trace_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    tool_calls_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    retrieved_chunks_json: Mapped[list[dict]] = mapped_column(JSON, nullable=False, default=list)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
