from dataclasses import dataclass


@dataclass
class PlanResult:
    intent: str
    steps: list[str]


class TaskPlanner:
    quiz_keywords = [
        "选择题",
        "题目",
        "出题",
        "quiz",
        "可能考哪些题",
        "可能考什么题",
        "会考哪些题",
        "会考什么题",
        "预测题",
        "模拟题",
        "练习题",
        "题型",
    ]

    explicit_material_question_keywords = [
        "根据资料",
        "根据文档",
        "根据文件",
        "根据这份资料",
        "根据这个文件",
        "结合资料",
        "结合文档",
        "文中",
        "材料中",
        "这份资料里",
        "这个文件里",
        "上传的资料",
        "上传的文件",
    ]

    followup_material_question_keywords = [
        "它",
        "这份",
        "这个",
        "其中",
        "还带来",
        "还会",
        "还包括",
        "哪些问题",
        "哪些影响",
        "哪些原因",
    ]

    document_check_keywords = [
        "文件",
        "文档",
        "资料",
        "上传",
        "看到",
        "看见",
        "查看",
        "读取",
        "识别",
        "能看",
        "能查看",
        "能读到",
        "有没有看到",
    ]

    greeting_keywords = [
        "你好",
        "您好",
        "hi",
        "hello",
        "在吗",
        "你是谁",
        "你能做什么",
    ]

    summary_keywords = ["总结", "摘要", "概括", "梳理"]
    key_point_keywords = ["知识点", "重点提取", "核心要点", "关键点"]
    outline_keywords = ["提纲", "复习提纲", "大纲", "outline"]
    question_keywords = ["什么", "为什么", "如何", "哪些", "作用", "影响", "原因", "解释", "回答", "?", "？"]

    def plan(self, message: str, has_material: bool = False) -> PlanResult:
        lowered = message.lower()
        has_summary = self._contains_any(message, self.summary_keywords) or "summary" in lowered
        has_key_points = self._contains_any(message, self.key_point_keywords)
        has_outline = self._contains_any(message, self.outline_keywords)
        has_quiz = self._contains_any(message, self.quiz_keywords) or "quiz" in lowered
        has_document_check = has_material and self._contains_any(message, self.document_check_keywords)
        references_material = has_material and self._contains_any(message, self.explicit_material_question_keywords)
        followup_material_question = has_material and self._contains_any(message, self.followup_material_question_keywords)
        has_question = self._contains_any(message, self.question_keywords)
        is_greeting = self._contains_any(lowered, [item.lower() for item in self.greeting_keywords])

        if has_summary and has_quiz:
            return PlanResult(intent="summary_and_quiz", steps=["识别任务类型：总结+出题", "调用摘要工具", "调用出题工具"])
        if has_key_points:
            return PlanResult(intent="key_points", steps=["识别任务类型：知识点提取", "调用知识点工具"])
        if has_outline:
            return PlanResult(intent="study_outline", steps=["识别任务类型：复习提纲", "调用提纲工具"])
        if has_summary:
            return PlanResult(intent="summary", steps=["识别任务类型：总结", "调用摘要工具"])
        if has_quiz:
            return PlanResult(intent="quiz", steps=["识别任务类型：出题", "调用出题工具"])
        if has_document_check:
            return PlanResult(intent="document_check", steps=["识别任务类型：资料确认", "检查当前会话资料", "返回资料可见性结果"])
        if (references_material and has_question) or (followup_material_question and has_question):
            return PlanResult(intent="rag_answer", steps=["识别任务类型：资料追问", "检索相关资料片段", "生成基于资料的回答"])
        if is_greeting:
            return PlanResult(intent="assistant_chat", steps=["识别任务类型：自由对话", "直接生成助手回复"])
        return PlanResult(intent="unknown", steps=["识别任务类型：待进一步分析", "交给路由模型判断是否需要工具"])

    def build_steps_for_intent(self, intent: str) -> list[str]:
        mapping = {
            "assistant_chat": ["识别任务类型：自由对话", "直接生成助手回复"],
            "document_check": ["识别任务类型：资料确认", "检查当前会话资料", "返回资料可见性结果"],
            "summary": ["识别任务类型：总结", "调用摘要工具"],
            "quiz": ["识别任务类型：出题", "调用出题工具"],
            "summary_and_quiz": ["识别任务类型：总结+出题", "调用摘要工具", "调用出题工具"],
            "key_points": ["识别任务类型：知识点提取", "调用知识点工具"],
            "study_outline": ["识别任务类型：复习提纲", "调用提纲工具"],
            "rag_answer": ["识别任务类型：资料追问", "检索相关资料片段", "生成基于资料的回答"],
        }
        return mapping.get(intent, ["识别任务类型：待进一步分析", "交给路由模型判断是否需要工具"])

    def _contains_any(self, message: str, keywords: list[str]) -> bool:
        return any(keyword in message for keyword in keywords)
