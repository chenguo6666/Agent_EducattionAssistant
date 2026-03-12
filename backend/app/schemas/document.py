from datetime import datetime

from pydantic import BaseModel


class DocumentSummaryResponse(BaseModel):
    documentId: str
    sessionId: str
    fileName: str
    fileType: str
    fileSize: int
    extractionStatus: str
    snippet: str
    createdAt: datetime


class RetrievedChunkResponse(BaseModel):
    chunkId: int
    documentId: str
    fileName: str
    content: str
    score: float


class DocumentListResponse(BaseModel):
    sessionId: str
    documents: list[DocumentSummaryResponse]
