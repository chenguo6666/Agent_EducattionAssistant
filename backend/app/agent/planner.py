from dataclasses import dataclass


@dataclass
class PlanResult:
    intent: str
    steps: list[str]


class TaskPlanner:
    def plan(self, message: str) -> PlanResult:
        lowered = message.lower()
        
        # 检测各类任务意图
        has_summary = any(keyword in message for keyword in ["总结", "摘要", "概括", "提取", "知识点", "提纲", "梳理"]) or "summary" in lowered
        has_quiz = any(keyword in message for keyword in ["选择题", "题目", "出题", "quiz"]) or "quiz" in lowered
        has_translation = any(keyword in message for keyword in ["翻译", "translate", "英译", "中译"]) 
        has_polish = any(keyword in message for keyword in ["润色", "修改", "改进", "优化", "polish", "improve"]) 
        has_explanation = any(keyword in message for keyword in ["解释", "含义", "定义", "词义", "explain", "meaning"]) 
        has_comparison = any(keyword in message for keyword in ["对比", "比较", "区别", "联系", "compare", "difference"]) 

        # 组合意图判断
        if has_summary and has_quiz:
            return PlanResult(
                intent="summary_and_quiz",
                steps=["识别任务类型：总结+出题", "调用摘要工具", "调用出题工具"],
            )
        if has_translation:
            return PlanResult(intent="translation", steps=["识别任务类型：翻译", "调用翻译工具"])
        if has_polish:
            return PlanResult(intent="polish", steps=["识别任务类型：内容润色", "调用润色工具"])
        if has_explanation:
            return PlanResult(intent="explanation", steps=["识别任务类型：词义解释", "调用解释工具"])
        if has_comparison:
            return PlanResult(intent="comparison", steps=["识别任务类型：对比分析", "调用对比工具"])
        if has_summary:
            return PlanResult(intent="summary", steps=["识别任务类型：总结", "调用摘要工具"])
        if has_quiz:
            return PlanResult(intent="quiz", steps=["识别任务类型：出题", "调用出题工具"])
        return PlanResult(intent="unknown", steps=["未识别出明确任务，回退到摘要工具"])
