from __future__ import annotations

"""从项目 settings 构造 LangChain ChatOpenAI（与 LLMClient 同源 base_url / key / model）。"""

from langchain_openai import ChatOpenAI

from app.core.settings import settings


def _openai_compatible_v1_base() -> str:
    base = (settings.llm_base_url or "").rstrip("/")
    if base.endswith("/v1"):
        return base
    return f"{base}/v1"


def build_chat_openai_from_settings(*, temperature: float = 0.7) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.llm_api_key,
        base_url=_openai_compatible_v1_base(),
        model=settings.llm_model,
        temperature=temperature,
        timeout=settings.llm_timeout_s,
    )
