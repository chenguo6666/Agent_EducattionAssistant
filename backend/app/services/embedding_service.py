import json
import math
from json import JSONDecodeError
from urllib import error, request

from app.core.config import settings


class EmbeddingService:
    max_document_embeddings = 12

    def __init__(self) -> None:
        self.api_key = settings.gemini_api_key.strip()
        self.model = "text-embedding-004"

    @property
    def is_available(self) -> bool:
        return bool(self.api_key)

    def embed_documents(self, texts: list[str]) -> list[list[float] | None]:
        if not self.is_available or not texts:
            return [None for _ in texts]

        embeddings: list[list[float] | None] = []
        for index, text in enumerate(texts):
            if index >= self.max_document_embeddings:
                embeddings.append(None)
                continue
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
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:embedContent"
        payload = json.dumps(
            {
                "model": f"models/{self.model}",
                "taskType": task_type,
                "content": {
                    "parts": [{"text": text[:8000]}],
                },
            }
        ).encode("utf-8")
        headers = {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }
        http_request = request.Request(url=url, data=payload, headers=headers, method="POST")

        try:
            with request.urlopen(http_request, timeout=10) as response:
                data = json.loads(response.read().decode("utf-8"))
        except (error.URLError, TimeoutError, JSONDecodeError):
            return None

        embedding = data.get("embedding", {})
        values = embedding.get("values", [])
        if not isinstance(values, list) or not values:
            return None
        return [float(value) for value in values]
