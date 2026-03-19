from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.models.document_chunk import DocumentChunk
from app.schemas.document import DocumentSummaryResponse, RetrievedChunkResponse
from app.services.document_service import DocumentService
from app.services.llm_service import LLMService
from app.services.retrieval_service import RetrievalService
from app.tools.quiz_tool import generate_quiz
from app.tools.summary_tool import summarize_text

TOOL_DISPLAY_NAMES: dict[str, str] = {
    "generate_summary_and_quiz": "综合任务工具",
    "summarize_material": "摘要工具",
    "generate_quiz": "出题工具",
    "extract_key_points": "知识点工具",
    "build_study_outline": "提纲工具",
    "retrieve_document_chunks": "资料检索工具",
    "answer_with_context": "资料问答工具",
}


def summarize_payload(value: Any, limit: int = 140) -> str:
    if value is None:
        return "无输出"
    text = ""
    if isinstance(value, str):
        text = value
    elif isinstance(value, dict):
        parts: list[str] = []
        for key, item in value.items():
            if key == "quiz" and isinstance(item, list):
                parts.append(f"quiz={len(item)}题")
                continue
            if key == "retrievedChunks" and isinstance(item, list):
                parts.append(f"retrieved={len(item)}段")
                continue
            rendered = str(item)
            if rendered:
                parts.append(f"{key}={rendered}")
        text = "; ".join(parts)
    elif isinstance(value, list):
        text = f"list[{len(value)}]"
    else:
        text = str(value)

    normalized = " ".join(text.split())
    if len(normalized) <= limit:
        return normalized
    return f"{normalized[:limit]}..."


def infer_quiz_count(message: str, default: int = 5) -> int:
    matched = re.search(r"(\d+)\s*个?\s*(选择题|题目)", message)
    if matched:
        return max(1, min(int(matched.group(1)), 10))
    digit_match = re.search(r"(\d+)", message)
    if digit_match:
        return max(1, min(int(digit_match.group(1)), 10))
    return default


@dataclass
class AgentExecutionContext:
    db: Session
    user_id: int
    session_id: str
    message: str
    material_text: str
    used_documents: list[DocumentSummaryResponse]
    recent_messages: list[str]
    llm_service: LLMService
    retrieval_service: RetrievalService
    document_service: DocumentService
    retrieved_chunks: list[RetrievedChunkResponse] = field(default_factory=list)
    retrieved_context_text: str = ""
    result_bundle: dict[str, Any] = field(default_factory=lambda: {"summary": None, "quiz": None, "answer": None})


class SummarizeMaterialArgs(BaseModel):
    task: str = Field(description="用户当前的总结任务描述")


class GenerateQuizArgs(BaseModel):
    task: str = Field(description="用户当前的出题任务描述")
    count: int = Field(default=5, ge=1, le=10, description="需要生成的题目数量")


class ExtractKeyPointsArgs(BaseModel):
    task: str = Field(description="用户当前的知识点提取任务描述")
    count: int = Field(default=6, ge=3, le=12, description="知识点条目数量")


class BuildStudyOutlineArgs(BaseModel):
    task: str = Field(description="用户当前的提纲生成任务描述")


class RetrieveDocumentChunksArgs(BaseModel):
    query: str = Field(description="需要在当前会话资料中检索的问题或主题")
    top_k: int = Field(default=4, ge=1, le=6, description="返回的最相关资料片段数量")


class AnswerWithContextArgs(BaseModel):
    question: str = Field(description="需要基于当前资料回答的问题")


class EducationToolbox:
    def __init__(self, context: AgentExecutionContext) -> None:
        self.context = context

    def build_langchain_tools(self) -> list[StructuredTool]:
        return [
            StructuredTool.from_function(
                func=self.summarize_material,
                name="summarize_material",
                description="总结当前会话资料，适用于摘要、概括、重点梳理任务。",
                args_schema=SummarizeMaterialArgs,
            ),
            StructuredTool.from_function(
                func=self.generate_quiz,
                name="generate_quiz",
                description="基于当前会话资料生成选择题，适用于练习题和考试准备任务。",
                args_schema=GenerateQuizArgs,
            ),
            StructuredTool.from_function(
                func=self.extract_key_points,
                name="extract_key_points",
                description="提取当前会话资料中的核心知识点。",
                args_schema=ExtractKeyPointsArgs,
            ),
            StructuredTool.from_function(
                func=self.build_study_outline,
                name="build_study_outline",
                description="基于当前会话资料生成复习提纲或学习大纲。",
                args_schema=BuildStudyOutlineArgs,
            ),
            StructuredTool.from_function(
                func=self.retrieve_document_chunks,
                name="retrieve_document_chunks",
                description="从当前会话资料中检索与问题最相关的片段。",
                args_schema=RetrieveDocumentChunksArgs,
            ),
            StructuredTool.from_function(
                func=self.answer_with_context,
                name="answer_with_context",
                description="基于当前已检索到的资料片段回答问题。",
                args_schema=AnswerWithContextArgs,
            ),
        ]

    def summarize_material(self, task: str) -> dict[str, Any]:
        material = self._build_generation_material(task=task)
        summary = self.context.llm_service.summarize(task=task, material=material) or summarize_text(material)
        self.context.result_bundle["summary"] = summary
        return {"summary": summary}

    def generate_summary_and_quiz(self, task: str, count: int = 5) -> dict[str, Any]:
        material = self._build_generation_material(task=task)
        combined = self.context.llm_service.generate_summary_and_quiz(task=task, material=material, count=count)
        if combined:
            summary, quiz = combined
        else:
            summary = self.context.llm_service.summarize(task=task, material=material) or summarize_text(material)
            quiz_material = summary if summary else material
            quiz = self.context.llm_service.generate_quiz(task=task, material=quiz_material, count=count) or generate_quiz(quiz_material, count=count)

        self.context.result_bundle["summary"] = summary
        self.context.result_bundle["quiz"] = quiz
        return {"summary": summary, "quiz": quiz}

    def generate_quiz(self, task: str, count: int = 5) -> dict[str, Any]:
        material = self._build_generation_material(task=task, prefer_summary=True)
        quiz = self.context.llm_service.generate_quiz(task=task, material=material, count=count) or generate_quiz(material, count=count)
        self.context.result_bundle["quiz"] = quiz
        return {"quiz": quiz}

    def extract_key_points(self, task: str, count: int = 6) -> dict[str, Any]:
        material = self._build_generation_material(task=task)
        answer = self.context.llm_service.extract_key_points(task=task, material=material, count=count) or self._build_local_key_points(material, count)
        self.context.result_bundle["answer"] = answer
        return {"answer": answer}

    def build_study_outline(self, task: str) -> dict[str, Any]:
        material = self._build_generation_material(task=task)
        answer = self.context.llm_service.build_study_outline(task=task, material=material) or self._build_local_outline(material)
        self.context.result_bundle["answer"] = answer
        return {"answer": answer}

    def retrieve_document_chunks(self, query: str, top_k: int = 4) -> dict[str, Any]:
        chunks = self.context.retrieval_service.retrieve(
            db=self.context.db,
            user_id=self.context.user_id,
            session_id=self.context.session_id,
            query=query,
            top_k=top_k,
        )
        self.context.retrieved_chunks = chunks
        self.context.retrieved_context_text = self.context.retrieval_service.build_context_text(chunks)
        return {
            "retrievedChunks": [chunk.model_dump() for chunk in chunks],
            "contextText": self.context.retrieved_context_text,
        }

    def answer_with_context(self, question: str) -> dict[str, Any]:
        context_text = self.context.retrieved_context_text or self._build_generation_material(task=question)
        answer = self.context.llm_service.answer_question(question=question, context=context_text) or self._build_local_answer(question, context_text)
        self.context.result_bundle["answer"] = answer
        return {"answer": answer}

    def _build_generation_material(self, task: str, prefer_summary: bool = False) -> str:
        summary = self.context.result_bundle.get("summary")
        if prefer_summary and isinstance(summary, str) and summary.strip():
            return summary
        if self.context.retrieved_context_text.strip():
            return self.context.retrieved_context_text

        focused_context = self._retrieve_private_context(task=task)
        if focused_context:
            return focused_context

        if self.context.material_text.strip():
            return self.context.material_text
        return self.context.message

    def _retrieve_private_context(self, task: str, top_k: int = 6) -> str:
        if not self.context.used_documents:
            return ""

        try:
            chunks = self.context.retrieval_service.retrieve(
                db=self.context.db,
                user_id=self.context.user_id,
                session_id=self.context.session_id,
                query=task,
                top_k=top_k,
            )
        except Exception:
            chunks = []

        parts = [chunk.content for chunk in chunks if chunk.content.strip()]
        if len(parts) < 3:
            parts.extend(self._sample_session_chunks(limit=max(top_k - len(parts), 0)))

        normalized_parts: list[str] = []
        seen: set[str] = set()
        for part in parts:
            normalized = " ".join(part.split()).strip()
            if not normalized or normalized in seen:
                continue
            seen.add(normalized)
            normalized_parts.append(normalized)

        return "\n\n".join(normalized_parts[:top_k]).strip()

    def _sample_session_chunks(self, limit: int = 4) -> list[str]:
        if limit <= 0:
            return []

        rows = (
            self.context.db.query(DocumentChunk.content)
            .filter(DocumentChunk.session_id == self.context.session_id, DocumentChunk.user_id == self.context.user_id)
            .order_by(DocumentChunk.chunk_index.asc(), DocumentChunk.id.asc())
            .limit(max(limit * 2, 8))
            .all()
        )
        sampled: list[str] = []
        for row in rows:
            content = row[0].strip()
            if len(content) < 20:
                continue
            sampled.append(content)
            if len(sampled) >= limit:
                break
        return sampled

    def _extract_candidate_points(self, material: str, limit: int) -> list[str]:
        normalized = re.sub(r"\s+", " ", material.replace("\r", "\n")).strip()
        sentences = re.split(r"[。！？；\n]", normalized)
        picked: list[str] = []
        for sentence in sentences:
            cleaned = sentence.replace("核心内容：", "").replace("-", " ").strip(" -:：;；,.，、")
            if len(cleaned) < 8:
                continue
            if cleaned in picked:
                continue
            picked.append(cleaned)
            if len(picked) >= limit:
                break
        return picked

    def _build_local_key_points(self, material: str, count: int) -> str:
        points = self._extract_candidate_points(material, count)
        if not points:
            return "1. 当前资料信息较少，建议补充更完整的学习内容。\n2. 可以尝试先让我总结资料，再继续提取知识点。"
        return "\n".join(f"{index + 1}. {point}" for index, point in enumerate(points))

    def _build_local_outline(self, material: str) -> str:
        points = self._extract_candidate_points(material, 4)
        if not points:
            return "一、核心内容梳理\n1. 明确资料主题\n2. 提炼主要观点\n\n二、复习建议\n1. 先整体浏览\n2. 再按主题回顾"
        outline_lines = ["一、核心主题"]
        outline_lines.extend(f"{index + 1}. {point}" for index, point in enumerate(points))
        outline_lines.extend(["", "二、复习建议", "1. 先按主题理解整体结构", "2. 再结合题目练习巩固重点", "3. 最后回顾易混淆内容"])
        return "\n".join(outline_lines)

    def _build_local_answer(self, question: str, context_text: str) -> str:
        points = self._extract_candidate_points(context_text, 3)
        if not points:
            return self.context.llm_service.chat(message=question, history_messages=self.context.recent_messages) or "我可以继续帮你细化这个问题，请补充更具体的资料或目标。"
        return "根据当前资料，可以先关注以下几点：\n" + "\n".join(f"- {point}" for point in points)
