import json
import math
from json import JSONDecodeError
from urllib import error, request

from app.core.config import settings


class EmbeddingService:
    def __init__(self) -> None:
        self.api_key = settings.embedding_api_key.strip()
        self.model = settings.embedding_model.strip()
        self.base_url = settings.embedding_base_url.strip()

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float] | None]:
        if not self.is_available or not texts:
            return [None for _ in texts]

        embeddings: list[list[float] | None] = []
        for text in texts:
            embeddings.append(self._embed(text=text, task_type="RETRIEVAL_DOCUMENT"))
        return embeddings

    def embed_query(self, text: str) -> list[float] | None:
        if not self.is_available or not text.strip():
            return None
        return self._embed(text=text, task_type="RETRIEVAL_QUERY")

    def cosine_similarity(self, left: list[float] | None, right: list[float] | None) -> float:
        if not left or not right or len(left) != len(right):
            return 0.0
        numerator = sum(x * y for x, y in zip(left, right))
        left_norm = math.sqrt(sum(x * x for x in left))
        right_norm = math.sqrt(sum(y * y for y in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        return numerator / (left_norm * right_norm)

    def _embed(self, text: str, task_type: str) -> list[float] | None:
        if not self.api_key or not self.model or not self.base_url:
            return None
        url = f"{self.base_url.rstrip('/')}/embeddings"
        payload = json.dumps(
            {
                "model": self.model,
                "input": text[:8000],
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        http_request = request.Request(url=url, data=payload, headers=headers, method="POST")

        try:
            with request.urlopen(http_request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, JSONDecodeError):
            return None

        items = data.get("data", [])
        values = items[0].get("embedding", []) if items and isinstance(items[0], dict) else []
        if not isinstance(values, list) or not values:
            return None
        return [float(value) for value in values]
