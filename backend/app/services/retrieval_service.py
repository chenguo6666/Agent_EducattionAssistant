import re

from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.models.uploaded_document import UploadedDocument
from app.schemas.document import RetrievedChunkResponse
from app.services.embedding_service import EmbeddingService


class RetrievalService:
    def __init__(self) -> None:
        self.embedding_service = EmbeddingService()

    def retrieve(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        query: str,
        top_k: int = 4,
    ) -> list[RetrievedChunkResponse]:
        chunk_rows = (
            db.query(DocumentChunk, UploadedDocument.file_name)
            .join(UploadedDocument, UploadedDocument.id == DocumentChunk.document_id)
            .filter(DocumentChunk.session_id == session_id, DocumentChunk.user_id == user_id)
            .order_by(DocumentChunk.id.asc())
            .all()
        )
        if not chunk_rows:
            return []

        query_terms = self._tokenize(query)
        query_embedding = self.embedding_service.embed_query(query)
        scored: list[tuple[RetrievedChunkResponse, float, float]] = []

        for chunk, file_name in chunk_rows:
            keyword_score = self._keyword_score(query=query, query_terms=query_terms, chunk=chunk)
            vector_score = self.embedding_service.cosine_similarity(query_embedding, chunk.embedding_json)
            final_score = keyword_score * 0.55 + max(vector_score, 0.0) * 8.0
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
        return self._tokenize(text)

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

    def _tokenize(self, text: str) -> list[str]:
        normalized = " ".join(text.split())
        chinese_sequences = re.findall(r"[\u4e00-\u9fff]{2,}", normalized)
        english_terms = re.findall(r"[A-Za-z][A-Za-z0-9_-]{2,}", normalized.lower())

        tokens: list[str] = []
        for sequence in chinese_sequences:
            for index in range(len(sequence) - 1):
                token = sequence[index : index + 2]
                if token not in tokens:
                    tokens.append(token)
            if sequence not in tokens:
                tokens.append(sequence)

        for term in english_terms:
            if term not in tokens:
                tokens.append(term)

        return tokens[:40]
