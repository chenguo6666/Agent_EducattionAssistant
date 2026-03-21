from __future__ import annotations

from typing import Any

from langchain_core.callbacks.base import BaseCallbackHandler

from app.agent.tools import TOOL_DISPLAY_NAMES, summarize_payload


class AgentTraceCollector(BaseCallbackHandler):
    def __init__(self) -> None:
        self.tool_calls: list[dict[str, Any]] = []

    def on_tool_start(self, serialized: dict[str, Any], input_str: str, **kwargs: Any) -> Any:
        tool_name = serialized.get("name", "tool")
        self.tool_calls.append(
            {
                "toolName": tool_name,
                "displayName": TOOL_DISPLAY_NAMES.get(tool_name, tool_name),
                "status": "running",
                "inputSummary": summarize_payload(input_str),
                "outputSummary": None,
            }
        )

    def on_tool_end(self, output: Any, **kwargs: Any) -> Any:
        tool_call = self._get_latest_running_tool()
        if tool_call is None:
            return
        tool_call["status"] = "completed"
        tool_call["outputSummary"] = summarize_payload(output)

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> Any:
        tool_call = self._get_latest_running_tool()
        if tool_call is None:
            return
        tool_call["status"] = "failed"
        tool_call["outputSummary"] = summarize_payload(str(error))

    def _get_latest_running_tool(self) -> dict[str, Any] | None:
        for item in reversed(self.tool_calls):
            if item.get("status") == "running":
                return item
        return None
