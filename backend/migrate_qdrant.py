from __future__ import annotations

from app.core.database import SessionLocal
from app.models.document_chunk import DocumentChunk
from app.rag.vector_stores.base import VectorPoint
from app.rag.vector_stores.factory import create_vector_store
from app.services.embedding_service import EmbeddingService


def migrate(batch_size: int = 32) -> int:
    db = SessionLocal()
    embedding_service = EmbeddingService()
    vector_store = create_vector_store()
    migrated = 0

    try:
        offset = 0
        while True:
            rows = (
                db.query(DocumentChunk)
                .order_by(DocumentChunk.id.asc())
                .offset(offset)
                .limit(batch_size)
                .all()
            )
            if not rows:
                break

            missing_indexes = [index for index, row in enumerate(rows) if not row.embedding_json]
            if missing_indexes:
                generated = embedding_service.embed_documents([rows[index].content for index in missing_indexes])
                for row_index, embedding in zip(missing_indexes, generated):
                    if embedding:
                        rows[row_index].embedding_json = embedding
                        db.add(rows[row_index])

            points: list[VectorPoint] = []
            for row in rows:
                if not row.embedding_json:
                    continue
                points.append(
                    VectorPoint(
                        chunk_id=row.id,
                        vector=list(row.embedding_json),
                        user_id=row.user_id,
                        session_id=row.session_id,
                        document_id=row.document_id,
                    )
                )

            vector_store.upsert_points(db=db, points=points)
            db.commit()
            migrated += len(points)
            offset += batch_size

        return migrated
    finally:
        db.close()


def main() -> None:
    migrated = migrate()
    print(f"Migrated {migrated} chunk vectors to the configured vector store.")


if __name__ == "__main__":
    main()
