from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.rag.vector_stores.base import VectorPoint, VectorSearchHit
from app.services.embedding_service import EmbeddingService


class SQLiteVectorStore:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    @property
    def is_available(self) -> bool:
        return True

    def upsert_points(self, db: Session, points: list[VectorPoint]) -> None:
        for point in points:
            row = db.query(DocumentChunk).filter(DocumentChunk.id == point.chunk_id).first()
            if row is None:
                continue
            row.embedding_json = point.vector
            db.add(row)

    def search(
        self,
        db: Session,
        query_vector: list[float] | None,
        *,
        user_id: int,
        session_id: str,
        limit: int,
    ) -> list[VectorSearchHit]:
        if not query_vector:
            return []

        rows = (
            db.query(DocumentChunk.id, DocumentChunk.embedding_json)
            .filter(DocumentChunk.user_id == user_id, DocumentChunk.session_id == session_id)
            .all()
        )
        hits: list[VectorSearchHit] = []
        for chunk_id, embedding in rows:
            score = self.embedding_service.cosine_similarity(query_vector, embedding)
            if score <= 0:
                continue
            hits.append(VectorSearchHit(chunk_id=chunk_id, score=score))

        return sorted(hits, key=lambda item: item.score, reverse=True)[:limit]

    def delete_document(self, db: Session, *, document_id: str) -> None:
        rows = db.query(DocumentChunk).filter(DocumentChunk.document_id == document_id).all()
        for row in rows:
            row.embedding_json = None
            db.add(row)
