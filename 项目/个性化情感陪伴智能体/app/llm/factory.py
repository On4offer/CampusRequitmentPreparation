"""从 settings 构造 LLMClient（供 routes 与 chat_turn 共用，测试可 monkeypatch routes._build_llm_client）。"""

from __future__ import annotations

from fastapi import HTTPException

from app.core.settings import settings
from app.llm.client import LLMClient


def build_llm_client() -> LLMClient:
    if not settings.llm_api_key:
        raise HTTPException(
            status_code=500,
            detail="Missing LLM_API_KEY. Create a .env file (see .env.example).",
        )
    return LLMClient(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        model=settings.llm_model,
        timeout_s=settings.llm_timeout_s,
    )
