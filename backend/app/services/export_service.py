from app.models.task_record import TaskRecord
from app.schemas.chat import ExportResponse
from app.schemas.document import RetrievedChunkResponse


class ExportService:
    def export_task_markdown(self, record: TaskRecord) -> ExportResponse:
        result = record.result_json or {}
        retrieved_chunks = [RetrievedChunkResponse(**item) for item in (record.retrieved_chunks_json or [])]

        lines = [
            "# 教育助手 AI Agent 导出结果",
            "",
            f"- 任务记录 ID：{record.id}",
            f"- 意图：{record.intent}",
            f"- 状态：{record.status}",
            "",
            "## 用户任务",
            "",
            record.message,
            "",
        ]

        summary = result.get("summary")
        answer = result.get("answer")
        quiz = result.get("quiz") or []

        if answer:
            lines.extend(["## 资料追问回答", "", str(answer), ""])

        if summary:
            lines.extend(["## 摘要结果", "", str(summary), ""])

        if quiz:
            lines.extend(["## 题目结果", ""])
            for index, item in enumerate(quiz, start=1):
                lines.append(f"### 题目 {index}")
                lines.append("")
                lines.append(str(item.get("question", "")))
                lines.append("")
                options = item.get("options", [])
                for option_index, option in enumerate(options):
                    option_letter = chr(65 + option_index)
                    lines.append(f"- {option_letter}. {option}")
                lines.append(f"- 答案：{item.get('answer', '')}")
                lines.append("")

        if retrieved_chunks:
            lines.extend(["## 资料来源", ""])
            for index, chunk in enumerate(retrieved_chunks, start=1):
                lines.append(f"### 片段 {index} - {chunk.fileName}")
                lines.append("")
                lines.append(chunk.content)
                lines.append("")

        return ExportResponse(
            fileName=f"task-record-{record.id}.md",
            content="\n".join(lines).strip() + "\n",
        )
