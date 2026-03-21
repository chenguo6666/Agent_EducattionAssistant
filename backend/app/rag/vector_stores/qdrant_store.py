from __future__ import annotations

import json
from json import JSONDecodeError
from urllib import error, request

from sqlalchemy.orm import Session

from app.core.config import settings
from app.rag.vector_stores.base import VectorPoint, VectorSearchHit


class QdrantVectorStore:
    def __init__(self) -> None:
        self.base_url = settings.vector_store_url.strip().rstrip("/")
        self.api_key = settings.vector_store_api_key.strip()
        self.collection = settings.vector_store_collection.strip() or "education_agent_chunks"
        self._collection_ready = False

    @property
    def is_available(self) -> bool:
        return bool(self.base_url)

    def upsert_points(self, db: Session, points: list[VectorPoint]) -> None:
        del db
        if not self.is_available or not points:
            return

        vector_size = len(points[0].vector) if points and points[0].vector else 0
        if vector_size <= 0:
            return
        if not self._ensure_collection(vector_size):
            return

        payload = {
            "points": [
                {
                    "id": point.chunk_id,
                    "vector": point.vector,
                    "payload": {
                        "chunk_id": point.chunk_id,
                        "user_id": point.user_id,
                        "session_id": point.session_id,
                        "document_id": point.document_id,
                    },
                }
                for point in points
                if point.vector
            ]
        }
        if not payload["points"]:
            return
        self._request("PUT", f"/collections/{self.collection}/points?wait=true", payload)

    def search(
        self,
        db: Session,
        query_vector: list[float] | None,
        *,
        user_id: int,
        session_id: str,
        limit: int,
    ) -> list[VectorSearchHit]:
        del db
        if not self.is_available or not query_vector:
            return []

        response = self._request(
            "POST",
            f"/collections/{self.collection}/points/search",
            {
                "vector": query_vector,
                "limit": limit,
                "with_payload": True,
                "filter": {
                    "must": [
                        {"key": "user_id", "match": {"value": user_id}},
                        {"key": "session_id", "match": {"value": session_id}},
                    ]
                },
            },
        )
        result = response.get("result", []) if isinstance(response, dict) else []
        hits: list[VectorSearchHit] = []
        for item in result:
            if not isinstance(item, dict):
                continue
            chunk_id = item.get("id")
            score = item.get("score")
            if isinstance(chunk_id, bool) or not isinstance(chunk_id, (int, float)) or not isinstance(score, (int, float)):
                continue
            hits.append(VectorSearchHit(chunk_id=int(chunk_id), score=float(score)))
        return hits

    def delete_document(self, db: Session, *, document_id: str) -> None:
        del db
        if not self.is_available:
            return
        self._request(
            "POST",
            f"/collections/{self.collection}/points/delete?wait=true",
            {"filter": {"must": [{"key": "document_id", "match": {"value": document_id}}]}},
        )

    def _ensure_collection(self, vector_size: int) -> bool:
        if self._collection_ready:
            return True

        response = self._request("GET", f"/collections/{self.collection}", None, tolerate_failure=True)
        if isinstance(response, dict) and response.get("result"):
            self._collection_ready = True
            return True

        created = self._request(
            "PUT",
            f"/collections/{self.collection}",
            {"vectors": {"size": vector_size, "distance": "Cosine"}},
            tolerate_failure=True,
        )
        self._collection_ready = isinstance(created, dict)
        return self._collection_ready

    def _request(
        self,
        method: str,
        path: str,
        payload: dict | None,
        tolerate_failure: bool = False,
    ) -> dict | None:
        if not self.base_url:
            return None

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["api-key"] = self.api_key

        body = json.dumps(payload).encode("utf-8") if payload is not None else None
        http_request = request.Request(url=f"{self.base_url}{path}", data=body, headers=headers, method=method)
        try:
            with request.urlopen(http_request, timeout=8) as response:
                raw = response.read().decode("utf-8")
        except (error.URLError, TimeoutError):
            if tolerate_failure:
                return None
            raise

        try:
            return json.loads(raw) if raw else {}
        except JSONDecodeError:
            return None if tolerate_failure else {}
