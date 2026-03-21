from __future__ import annotations

from app.core.config import settings
from app.rag.vector_stores.qdrant_store import QdrantVectorStore
from app.rag.vector_stores.sqlite_store import SQLiteVectorStore


def create_vector_store():
    provider = settings.vector_store_provider.strip().lower()
    if provider == "qdrant":
        store = QdrantVectorStore()
        if store.is_available:
            return store
    return SQLiteVectorStore()
