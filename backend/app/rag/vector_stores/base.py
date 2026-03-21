from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from sqlalchemy.orm import Session


@dataclass
class VectorPoint:
    chunk_id: int
    vector: list[float]
    user_id: int
    session_id: str
    document_id: str


@dataclass
class VectorSearchHit:
    chunk_id: int
    score: float


class VectorStore(Protocol):
    @property
    def is_available(self) -> bool:
        ...

    def upsert_points(self, db: Session, points: list[VectorPoint]) -> None:
        ...

    def search(
        self,
        db: Session,
        query_vector: list[float] | None,
        *,
        user_id: int,
        session_id: str,
        limit: int,
    ) -> list[VectorSearchHit]:
        ...

    def delete_document(self, db: Session, *, document_id: str) -> None:
        ...
