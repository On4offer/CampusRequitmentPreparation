from __future__ import annotations

"""从 LangChain `on_llm_end` 回调提取供应商 request id，供自研 Trace 与 SSE meta 使用。"""

from typing import Any
from uuid import UUID

from langchain_core.callbacks.base import BaseCallbackHandler
from langchain_core.outputs import LLMResult


def extract_provider_request_id(response: LLMResult) -> str | None:
    """优先 `AIMessage.response_metadata['id']`，其次 `llm_output['id']`。"""
    for group in response.generations or []:
        for g in group:
            msg = getattr(g, "message", None)
            if msg is not None:
                meta = getattr(msg, "response_metadata", None) or {}
                rid = meta.get("id")
                if isinstance(rid, str) and rid.strip():
                    return rid.strip()
    lo = response.llm_output
    if isinstance(lo, dict):
        rid = lo.get("id")
        if isinstance(rid, str) and rid.strip():
            return rid.strip()
    return None


class LlmProviderIdCallback(BaseCallbackHandler):
    """将解析到的 id 写入 `sink['request_id']`（与 httpx 路径 `meta_out` 字段名一致）。"""

    def __init__(self, sink: dict[str, Any]) -> None:
        self._sink = sink

    def on_llm_end(self, response: LLMResult, *, run_id: UUID, parent_run_id: UUID | None = None, **kwargs: Any) -> None:
        rid = extract_provider_request_id(response)
        if rid:
            self._sink["request_id"] = rid
