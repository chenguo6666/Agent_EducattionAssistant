import uuid

from app.schemas.chat import ChatResponse, ChatResult, TaskStage
from app.services.status import STATUS_ANALYZING, STATUS_COMPLETED, STATUS_EXECUTING, STATUS_SUBMITTED
from app.agent.planner import TaskPlanner
from app.tools.quiz_tool import generate_quiz
from app.tools.summary_tool import summarize_text


class ChatService:
    def __init__(self) -> None:
        self.planner = TaskPlanner()

    def execute(self, message: str) -> ChatResponse:
        plan = self.planner.plan(message)
        summary = None
        quiz = None

        if plan.intent in {"summary", "summary_and_quiz", "unknown"}:
            summary = summarize_text(message)

        if plan.intent in {"quiz", "summary_and_quiz"}:
            quiz = generate_quiz(message, count=5 if "5" in message else 3)

        timeline = [
            TaskStage(status=STATUS_SUBMITTED, label="任务已提交"),
            TaskStage(status=STATUS_ANALYZING, label="正在分析任务意图"),
            TaskStage(status=STATUS_EXECUTING, label="正在调用工具"),
            TaskStage(status=STATUS_COMPLETED, label="任务执行完成"),
        ]

        return ChatResponse(
            taskId=f"task_{uuid.uuid4().hex[:8]}",
            intent=plan.intent,
            status=STATUS_COMPLETED,
            steps=plan.steps,
            timeline=timeline,
            result=ChatResult(summary=summary, quiz=quiz),
        )
