from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.agent.callbacks import AgentTraceCollector
from app.agent.planner import PlanResult, TaskPlanner
from app.agent.tools import AgentExecutionContext, EducationToolbox, TOOL_DISPLAY_NAMES, infer_quiz_count, summarize_payload
from app.core.config import settings
from app.schemas.chat import AgentTraceItem, ChatResult, TaskStage, ToolCallItem
from app.schemas.document import DocumentSummaryResponse, RetrievedChunkResponse
from app.services.document_service import DocumentService
from app.services.gemini_service import GeminiService, RouteDecision
from app.services.retrieval_service import RetrievalService
from app.services.status import STATUS_ANALYZING, STATUS_COMPLETED, STATUS_EXECUTING, STATUS_FAILED, STATUS_SUBMITTED

INTENT_LABELS = {
    "assistant_chat": "自由对话",
    "summary": "摘要",
    "quiz": "出题",
    "summary_and_quiz": "综合任务",
    "key_points": "知识点提取",
    "study_outline": "复习提纲",
    "rag_answer": "资料追问",
    "document_check": "资料确认",
    "unknown": "待进一步分析",
}

TOOL_INTENTS = {"summary", "quiz", "summary_and_quiz", "key_points", "study_outline", "rag_answer"}


class AgentExecutionResult(BaseModel):
    intent: str
    status: str
    steps: list[str]
    timeline: list[TaskStage]
    result: ChatResult
    agent_trace: list[AgentTraceItem]
    tool_calls: list[ToolCallItem]
    retrieved_chunks: list[RetrievedChunkResponse]


class AgentOrchestrator:
    def __init__(self) -> None:
        self.planner = TaskPlanner()
        self.gemini_service = GeminiService()
        self.retrieval_service = RetrievalService()
        self.document_service = DocumentService()
        self.model_name = settings.gemini_model.strip() or "gemini-2.5-flash"

    def run(
        self,
        db: Session,
        user_id: int,
        session_id: str,
        message: str,
        material_text: str,
        used_documents: list[DocumentSummaryResponse],
        recent_messages: list[str],
    ) -> AgentExecutionResult:
        context = AgentExecutionContext(
            db=db,
            user_id=user_id,
            session_id=session_id,
            message=message,
            material_text=material_text,
            used_documents=used_documents,
            recent_messages=recent_messages,
            gemini_service=self.gemini_service,
            retrieval_service=self.retrieval_service,
            document_service=self.document_service,
        )
        toolbox = EducationToolbox(context)
        plan = self._route_message(context)

        if plan.intent == "unknown":
            if self.gemini_service.is_available:
                try:
                    return self._run_langchain_agent(toolbox=toolbox, context=context)
                except Exception:
                    pass
            return self._run_fallback(toolbox=toolbox, context=context, plan_intent="assistant_chat")

        return self._run_fallback(toolbox=toolbox, context=context, plan_intent=plan.intent)

    def _route_message(self, context: AgentExecutionContext) -> PlanResult:
        explicit_plan = self.planner.plan(context.message, has_material=bool(context.used_documents))
        if explicit_plan.intent != "unknown":
            return explicit_plan

        if not self.gemini_service.is_available:
            return PlanResult(intent="assistant_chat", steps=self.planner.build_steps_for_intent("assistant_chat"))

        decision = self.gemini_service.classify_task(
            message=context.message,
            has_material=bool(context.used_documents),
            history_messages=context.recent_messages,
            document_names=[document.fileName for document in context.used_documents],
        )
        if decision is None:
            return PlanResult(intent="assistant_chat", steps=self.planner.build_steps_for_intent("assistant_chat"))

        if decision.intent == "assistant_chat" or not decision.should_use_tools:
            return PlanResult(intent="assistant_chat", steps=self.planner.build_steps_for_intent("assistant_chat"))

        return PlanResult(intent=decision.intent, steps=self.planner.build_steps_for_intent(decision.intent))

    def _run_langchain_agent(self, toolbox: EducationToolbox, context: AgentExecutionContext) -> AgentExecutionResult:
        collector = AgentTraceCollector()
        llm = ChatGoogleGenerativeAI(
            model=self.model_name,
            api_key=settings.gemini_api_key,
            temperature=0.2,
            request_timeout=12,
            retries=1,
            max_tokens=800,
            thinking_budget=0,
        )
        tools = toolbox.build_langchain_tools()
        prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    (
                        "你是教育助手 AI Agent。"
                        "你可以根据用户任务决定是否调用工具。"
                        "如需处理摘要、出题、知识点提取、提纲或资料问答，请优先调用合适的工具。"
                        "复合任务可以串行调用多个工具。"
                        "不要暴露内部推理。"
                        "最终只输出一个 JSON 对象，包含 intent、summary、quiz、answer 四个字段。"
                        "intent 必须是 assistant_chat、summary、quiz、summary_and_quiz、key_points、study_outline、rag_answer 之一。"
                        "没有的字段填 null。"
                    ),
                ),
                (
                    "human",
                    (
                        "用户任务：{input}\n"
                        "当前会话是否有资料：{has_material}\n"
                        "当前资料数量：{document_count}\n"
                        "最近对话：\n{recent_history}\n"
                    ),
                ),
                MessagesPlaceholder("agent_scratchpad"),
            ]
        )
        agent = create_tool_calling_agent(llm=llm, tools=tools, prompt=prompt)
        executor = AgentExecutor(
            agent=agent,
            tools=tools,
            callbacks=[collector],
            verbose=False,
            max_iterations=3,
            handle_parsing_errors=True,
        )

        response = executor.invoke(
            {
                "input": context.message,
                "has_material": "是" if context.used_documents else "否",
                "document_count": str(len(context.used_documents)),
                "recent_history": "\n".join(f"- {item}" for item in context.recent_messages[-4:]) or "无",
            }
        )
        raw_output = str(response.get("output", "")).strip()
        payload = self._parse_final_payload(raw_output)
        intent = self._resolve_intent(payload.get("intent"), collector.tool_calls, context.used_documents, context.message)
        result = self._merge_result_bundle(context=context, payload=payload, raw_output=raw_output, intent=intent)
        tool_calls = [ToolCallItem(**item) for item in collector.tool_calls]
        agent_trace = self._build_agent_trace(intent=intent, tool_calls=tool_calls, failed=False)
        steps = self._build_steps(intent=intent, tool_calls=tool_calls)
        timeline = self._build_timeline(failed=False, tool_calls=tool_calls, intent=intent)

        return AgentExecutionResult(
            intent=intent,
            status=STATUS_COMPLETED,
            steps=steps,
            timeline=timeline,
            result=result,
            agent_trace=agent_trace,
            tool_calls=tool_calls,
            retrieved_chunks=context.retrieved_chunks,
        )

    def _run_fallback(
        self,
        toolbox: EducationToolbox,
        context: AgentExecutionContext,
        plan_intent: str | None = None,
    ) -> AgentExecutionResult:
        plan = self.planner.plan(context.message, has_material=bool(context.used_documents))
        if plan_intent:
            plan.intent = plan_intent
            plan.steps = self.planner.build_steps_for_intent(plan.intent)

        tool_calls: list[ToolCallItem] = []
        failed = False

        def run_tool(name: str, **kwargs: Any) -> dict[str, Any]:
            method = getattr(toolbox, name)
            input_summary = summarize_payload(kwargs)
            try:
                output = method(**kwargs)
            except Exception as error:
                nonlocal failed
                failed = True
                tool_calls.append(
                    ToolCallItem(
                        toolName=name,
                        displayName=TOOL_DISPLAY_NAMES.get(name, name),
                        status="failed",
                        inputSummary=input_summary,
                        outputSummary=summarize_payload(str(error)),
                    )
                )
                raise

            tool_calls.append(
                ToolCallItem(
                    toolName=name,
                    displayName=TOOL_DISPLAY_NAMES.get(name, name),
                    status="completed",
                    inputSummary=input_summary,
                    outputSummary=summarize_payload(output),
                )
            )
            return output

        if plan.intent == "summary_and_quiz":
            run_tool("summarize_material", task=context.message)
            run_tool("generate_quiz", task=context.message, count=infer_quiz_count(context.message))
        elif plan.intent == "summary":
            run_tool("summarize_material", task=context.message)
        elif plan.intent == "quiz":
            run_tool("generate_quiz", task=context.message, count=infer_quiz_count(context.message))
        elif plan.intent == "key_points":
            run_tool("extract_key_points", task=context.message, count=6)
        elif plan.intent == "study_outline":
            run_tool("build_study_outline", task=context.message)
        elif plan.intent == "rag_answer":
            run_tool("retrieve_document_chunks", query=context.message, top_k=4)
            run_tool("answer_with_context", question=context.message)
        elif plan.intent == "document_check":
            file_names = [document.fileName for document in context.used_documents]
            if file_names:
                joined_names = "、".join(file_names[:3])
                extra = f" 等 {len(file_names)} 份资料。" if len(file_names) > 3 else "。"
                context.result_bundle["answer"] = (
                    f"可以，我已经读取到当前会话资料：{joined_names}{extra}"
                    "你可以继续让我总结、提取知识点、生成复习提纲、出题，或者根据资料回答问题。"
                )
            else:
                context.result_bundle["answer"] = "当前会话还没有挂载资料。你可以先点击 + 上传文件，然后再让我根据资料处理任务。"
        else:
            answer = self.gemini_service.chat(message=context.message, history_messages=context.recent_messages)
            if not answer:
                answer = "我可以帮你完成学习问答、资料总结、知识点提取、复习提纲和选择题生成。请继续描述你的任务。"
            context.result_bundle["answer"] = answer

        result = ChatResult(
            summary=context.result_bundle.get("summary"),
            quiz=context.result_bundle.get("quiz"),
            answer=context.result_bundle.get("answer"),
        )
        agent_trace = self._build_agent_trace(intent=plan.intent, tool_calls=tool_calls, failed=failed)
        steps = self._build_steps(intent=plan.intent, tool_calls=tool_calls)
        timeline = self._build_timeline(failed=failed, tool_calls=tool_calls, intent=plan.intent)

        return AgentExecutionResult(
            intent=plan.intent,
            status=STATUS_FAILED if failed else STATUS_COMPLETED,
            steps=steps,
            timeline=timeline,
            result=result,
            agent_trace=agent_trace,
            tool_calls=tool_calls,
            retrieved_chunks=context.retrieved_chunks,
        )

    def _parse_final_payload(self, output: str) -> dict[str, Any]:
        if not output:
            return {}
        normalized = output.strip()
        if normalized.startswith("```") and normalized.endswith("```"):
            lines = normalized.splitlines()
            normalized = "\n".join(lines[1:-1]).strip()
        try:
            payload = json.loads(normalized)
        except JSONDecodeError:
            return {"answer": normalized}
        return payload if isinstance(payload, dict) else {"answer": normalized}

    def _merge_result_bundle(self, context: AgentExecutionContext, payload: dict[str, Any], raw_output: str, intent: str) -> ChatResult:
        summary = payload.get("summary") if isinstance(payload.get("summary"), str) else context.result_bundle.get("summary")
        quiz_payload = payload.get("quiz")
        quiz = quiz_payload if isinstance(quiz_payload, list) else context.result_bundle.get("quiz")
        answer = payload.get("answer") if isinstance(payload.get("answer"), str) else context.result_bundle.get("answer")

        if intent == "assistant_chat" and not answer:
            answer = raw_output
        if intent in {"key_points", "study_outline", "rag_answer"} and not answer:
            answer = raw_output

        return ChatResult(summary=summary, quiz=quiz, answer=answer)

    def _resolve_intent(
        self,
        raw_intent: Any,
        tool_calls: list[dict[str, Any]] | list[ToolCallItem],
        used_documents: list[DocumentSummaryResponse],
        message: str,
    ) -> str:
        valid_intents = set(INTENT_LABELS.keys()) - {"unknown"}
        if isinstance(raw_intent, str) and raw_intent in valid_intents:
            return raw_intent

        tool_names = [item["toolName"] if isinstance(item, dict) else item.toolName for item in tool_calls]
        if "summarize_material" in tool_names and "generate_quiz" in tool_names:
            return "summary_and_quiz"
        if "extract_key_points" in tool_names:
            return "key_points"
        if "build_study_outline" in tool_names:
            return "study_outline"
        if "retrieve_document_chunks" in tool_names or "answer_with_context" in tool_names:
            return "rag_answer"
        if "generate_quiz" in tool_names:
            return "quiz"
        if "summarize_material" in tool_names:
            return "summary"

        rule_plan = self.planner.plan(message, has_material=bool(used_documents))
        return "assistant_chat" if rule_plan.intent == "unknown" else rule_plan.intent

    def _build_agent_trace(self, intent: str, tool_calls: list[ToolCallItem], failed: bool) -> list[AgentTraceItem]:
        trace: list[AgentTraceItem] = [
            AgentTraceItem(
                type="analysis",
                label="识别任务意图",
                status="completed" if not failed else "failed",
                summary=f"已识别为 {INTENT_LABELS.get(intent, intent)}",
            )
        ]
        trace.extend(
            AgentTraceItem(
                type="tool",
                label=f"调用工具：{call.displayName}",
                status=call.status,
                summary=call.outputSummary or call.inputSummary,
            )
            for call in tool_calls
        )
        trace.append(
            AgentTraceItem(
                type="final",
                label="整理最终结果",
                status="failed" if failed else "completed",
                summary="任务执行失败，请稍后重试。" if failed else "结果已生成并返回前端。",
            )
        )
        return trace

    def _build_steps(self, intent: str, tool_calls: list[ToolCallItem]) -> list[str]:
        steps = [f"识别任务类型：{INTENT_LABELS.get(intent, intent)}"]
        steps.extend(f"调用工具：{call.displayName}" for call in tool_calls)
        if not tool_calls and intent == "assistant_chat":
            steps.append("直接生成助手回复")
        if not tool_calls and intent == "document_check":
            steps.append("检查当前会话资料")
        steps.append("整理最终结果")
        return steps

    def _build_timeline(self, failed: bool, tool_calls: list[ToolCallItem], intent: str) -> list[TaskStage]:
        if failed:
            return [
                TaskStage(status=STATUS_SUBMITTED, label="任务已提交"),
                TaskStage(status=STATUS_ANALYZING, label="分析中"),
                TaskStage(status=STATUS_EXECUTING, label="执行失败"),
                TaskStage(status=STATUS_FAILED, label="任务失败"),
            ]

        executing_label = "正在调用工具" if tool_calls or intent in TOOL_INTENTS else "正在生成回复"
        return [
            TaskStage(status=STATUS_SUBMITTED, label="任务已提交"),
            TaskStage(status=STATUS_ANALYZING, label="正在分析任务意图"),
            TaskStage(status=STATUS_EXECUTING, label=executing_label),
            TaskStage(status=STATUS_COMPLETED, label="任务执行完成"),
        ]
