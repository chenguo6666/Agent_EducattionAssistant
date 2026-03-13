from dataclasses import dataclass


@dataclass
class PlanResult:
    intent: str
    steps: list[str]


class TaskPlanner:
    def plan(self, message: str) -> PlanResult:
        lowered = message.lower()
        has_summary = any(keyword in message for keyword in ["总结", "摘要", "概括", "提取", "知识点", "提纲", "梳理"]) or "summary" in lowered
        has_quiz = any(keyword in message for keyword in ["选择题", "题目", "出题", "quiz"]) or "quiz" in lowered

        if has_summary and has_quiz:
            return PlanResult(
                intent="summary_and_quiz",
                steps=["识别任务类型：总结+出题", "调用摘要工具", "调用出题工具"],
            )
        if has_summary:
            return PlanResult(intent="summary", steps=["识别任务类型：总结", "调用摘要工具"])
        if has_quiz:
            return PlanResult(intent="quiz", steps=["识别任务类型：出题", "调用出题工具"])
        return PlanResult(intent="unknown", steps=["未识别出明确任务，回退到摘要工具"])
