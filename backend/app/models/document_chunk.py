from sqlalchemy import ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    document_id: Mapped[str] = mapped_column(ForeignKey("uploaded_documents.id"), nullable=False, index=True)
    session_id: Mapped[str] = mapped_column(ForeignKey("chat_sessions.id"), nullable=False, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    keywords_json: Mapped[list[str]] = mapped_column(JSON, nullable=False, default=list)
    embedding_json: Mapped[list[float] | None] = mapped_column(JSON, nullable=True)
