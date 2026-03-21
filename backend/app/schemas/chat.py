from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.schemas.document import DocumentSummaryResponse, RetrievedChunkResponse

TaskStatus = Literal["submitted", "analyzing", "executing", "completed", "failed"]
TraceStatus = Literal["pending", "running", "completed", "failed"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)
    sessionId: str | None = Field(default=None, max_length=36)

    @field_validator("message")
    @classmethod
    def validate_message(cls, value: str) -> str:
        normalized = value.strip()
        if len(normalized) < 2:
            raise ValueError("任务内容过短")
        return normalized


class QuizItem(BaseModel):
    question: str
    options: list[str]
    answer: str


class QuizAnswerItem(BaseModel):
    questionIndex: int
    userAnswer: str


class TaskStage(BaseModel):
    status: TaskStatus
    label: str


class AgentTraceItem(BaseModel):
    type: Literal["analysis", "tool", "final"]
    label: str
    status: TraceStatus
    summary: str | None = None


class ToolCallItem(BaseModel):
    toolName: str
    displayName: str
    status: TraceStatus
    inputSummary: str | None = None
    outputSummary: str | None = None


class ChatResult(BaseModel):
    summary: str | None = None
    quiz: list[QuizItem] | None = None
    answer: str | None = None


class ChatResponse(BaseModel):
    taskId: str
    recordId: int
    sessionId: str
    intent: str
    status: TaskStatus
    steps: list[str]
    timeline: list[TaskStage]
    result: ChatResult
    agentTrace: list[AgentTraceItem] = Field(default_factory=list)
    toolCalls: list[ToolCallItem] = Field(default_factory=list)
    usedDocuments: list[DocumentSummaryResponse] = Field(default_factory=list)
    retrievedChunks: list[RetrievedChunkResponse] = Field(default_factory=list)


class TaskRecordResponse(BaseModel):
    id: int
    message: str
    intent: str
    status: TaskStatus
    steps: list[str]
    timeline: list[TaskStage]
    result: ChatResult
    agentTrace: list[AgentTraceItem] = Field(default_factory=list)
    toolCalls: list[ToolCallItem] = Field(default_factory=list)
    retrievedChunks: list[RetrievedChunkResponse] = Field(default_factory=list)
    errorMessage: str | None = None
    createdAt: datetime


class ChatSessionSummary(BaseModel):
    sessionId: str
    title: str
    lastMessage: str
    lastStatus: TaskStatus | None = None
    createdAt: datetime
    updatedAt: datetime


class ChatSessionListResponse(BaseModel):
    sessions: list[ChatSessionSummary]


class ChatSessionDetailResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    sessionId: str
    title: str
    createdAt: datetime
    updatedAt: datetime
    tasks: list[TaskRecordResponse]
    documents: list[DocumentSummaryResponse]


class ExportResponse(BaseModel):
    fileName: str
    content: str


class QuizAttemptRequest(BaseModel):
    answers: list[QuizAnswerItem]


class QuizAttemptResponse(BaseModel):
    savedMistakes: int
    totalQuestions: int
    correctCount: int
    message: str


class MistakeItemResponse(BaseModel):
    id: int
    sessionId: str
    taskRecordId: int
    question: str
    options: list[str]
    correctAnswer: str
    userAnswer: str
    sourceExcerpt: str | None = None
    createdAt: datetime


class MistakeListResponse(BaseModel):
    items: list[MistakeItemResponse]
