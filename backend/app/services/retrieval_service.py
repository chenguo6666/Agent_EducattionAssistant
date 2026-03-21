from __future__ import annotations

from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document_chunk import DocumentChunk
from app.models.uploaded_document import UploadedDocument
from app.rag.text import tokenize_text
from app.rag.vector_stores.factory import create_vector_store
from app.schemas.document import RetrievedChunkResponse
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()
        self.vector_store = create_vector_store()

    def retrieve(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        query: str,
        top_k: int = 4,
    ) -> list[RetrievedChunkResponse]:
        chunk_rows = self._load_candidates(
            db=db,
            user_id=user_id,
            session_id=session_id,
            limit=max(top_k * 4, settings.retrieval_candidate_limit),
        )
        if not chunk_rows:
            return []

        query_terms = tokenize_text(query)
        query_embedding = self.embedding_service.embed_query(query)
        vector_hits = self.vector_store.search(
            db=db,
            query_vector=query_embedding,
            user_id=user_id,
            session_id=session_id,
            limit=max(top_k * 3, settings.retrieval_candidate_limit),
        )
        vector_scores = {item.chunk_id: max(item.score, 0.0) for item in vector_hits}

        scored: list[tuple[RetrievedChunkResponse, float, float]] = []
        for chunk, file_name in chunk_rows:
            keyword_score = self._keyword_score(query=query, query_terms=query_terms, chunk=chunk)
            vector_score = vector_scores.get(chunk.id, 0.0)
            final_score = self._hybrid_score(keyword_score=keyword_score, vector_score=vector_score)
            if final_score <= 0:
                continue
            scored.append(
                (
                    RetrievedChunkResponse(
                        chunkId=chunk.id,
                        documentId=chunk.document_id,
                        fileName=file_name,
                        content=chunk.content,
                        score=round(final_score, 3),
                    ),
                    keyword_score,
                    vector_score,
                )
            )

        if not scored:
            return [
                RetrievedChunkResponse(
                    chunkId=chunk.id,
                    documentId=chunk.document_id,
                    fileName=file_name,
                    content=chunk.content,
                    score=0.1,
                )
                for chunk, file_name in chunk_rows[:top_k]
            ]

        reranked = self._rerank(scored=scored, query_terms=query_terms)
        return [item for item, _, _ in reranked[:top_k]]

    def build_context_text(self, chunks: list[RetrievedChunkResponse]) -> str:
        context_parts = []
        for index, chunk in enumerate(chunks, start=1):
            context_parts.append(f"[片段 {index}] 来源：{chunk.fileName}\n{chunk.content}")
        return "\n\n".join(context_parts)

    def maybe_enrich_query(self, current_message: str, history_messages: list[str]) -> str:
        if not history_messages:
            return current_message

        normalized = current_message.strip()
        needs_context = (
            len(normalized) < 18
            or any(token in normalized for token in ["它", "这", "这些", "上述", "刚才", "前面", "该内容", "这个"])
        )
        if not needs_context:
            return normalized

        recent_history = "；".join(message.strip() for message in history_messages[-2:] if message.strip())
        if not recent_history:
            return normalized
        return f"{recent_history}；当前追问：{normalized}"

    def tokenize_text(self, text: str) -> list[str]:
        return tokenize_text(text)

    def _load_candidates(
        self,
        db: Session,
        *,
        user_id: int,
        session_id: str,
        limit: int,
    ) -> list[tuple[DocumentChunk, str]]:
        return (
            db.query(DocumentChunk, UploadedDocument.file_name)
            .join(UploadedDocument, UploadedDocument.id == DocumentChunk.document_id)
            .filter(DocumentChunk.session_id == session_id, DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.chunk_index.asc(), DocumentChunk.id.asc())
            .limit(limit)
            .all()
        )

    def _hybrid_score(self, *, keyword_score: float, vector_score: float) -> float:
        keyword_part = keyword_score * settings.retrieval_keyword_weight
        vector_part = max(vector_score, 0.0) * settings.retrieval_vector_weight * 10.0
        return keyword_part + vector_part

    def _rerank(
        self,
        scored: list[tuple[RetrievedChunkResponse, float, float]],
        query_terms: list[str],
    ) -> list[tuple[RetrievedChunkResponse, float, float]]:
        def rerank_key(item: tuple[RetrievedChunkResponse, float, float]) -> tuple[float, int, float]:
            chunk, keyword_score, vector_score = item
            term_coverage = sum(1 for term in query_terms if term and term in chunk.content)
            return (chunk.score + term_coverage * 0.4, term_coverage, vector_score)

        return sorted(scored, key=rerank_key, reverse=True)

    def _keyword_score(self, query: str, query_terms: list[str], chunk: DocumentChunk) -> float:
        content = chunk.content
        chunk_terms = list(chunk.keywords_json or [])
        overlap = len(set(query_terms) & set(chunk_terms))
        direct_hits = sum(1 for term in query_terms if term and term in content)
        phrase_bonus = 2 if query.strip() and query.strip() in content else 0
        return float(overlap * 2 + direct_hits + phrase_bonus)
