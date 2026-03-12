from typing import Literal

from pydantic import BaseModel, Field, field_validator

TaskStatus = Literal["submitted", "analyzing", "executing", "completed", "failed"]


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=2000)

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


class TaskStage(BaseModel):
    status: TaskStatus
    label: str


class ChatResult(BaseModel):
    summary: str | None = None
    quiz: list[QuizItem] | None = None
    translation: str | None = None
    polish: str | None = None
    explanation: str | None = None
    comparison: str | None = None


class ChatResponse(BaseModel):
    taskId: str
    intent: str
    status: TaskStatus
    steps: list[str]
    timeline: list[TaskStage]
    result: ChatResult
