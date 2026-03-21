from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.rag.vector_stores.base import VectorPoint
from app.rag.vector_stores.factory import create_vector_store
from app.services.embedding_service import EmbeddingService


class RagIngestionService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = create_vector_store()

    def index_chunks(self, db: Session, chunks: list[DocumentChunk]) -> None:
        if not chunks:
            return

        texts = [chunk.content for chunk in chunks]
        embeddings = self.embedding_service.embed_documents(texts)
        points: list[VectorPoint] = []

        for chunk, embedding in zip(chunks, embeddings):
            if embedding:
                chunk.embedding_json = embedding
            db.add(chunk)
            if not embedding:
                continue
            points.append(
                VectorPoint(
                    chunk_id=chunk.id,
                    vector=embedding,
                    user_id=chunk.user_id,
                    session_id=chunk.session_id,
                    document_id=chunk.document_id,
                )
            )

        self.vector_store.upsert_points(db=db, points=points)
