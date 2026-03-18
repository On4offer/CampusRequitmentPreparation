from __future__ import annotations

import time
import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import ChatRequest, ChatResponse, HealthResponse
from app.core.settings import settings
from app.llm.client import ChatMessage, LLMClient, LLMClientError


router = APIRouter()


def _build_llm_client() -> LLMClient:
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


@router.get("/health", response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse()


@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    t0 = time.perf_counter()
    trace_id = str(uuid.uuid4())

    system = (
        "你是一个温和、克制、尊重边界的情感陪伴助手。"
        "如果用户表达自伤/他伤倾向，你要进入安全模式：建议联系现实支持与专业帮助，避免给出危险建议。"
    )
    messages = [
        ChatMessage(role="system", content=system),
        ChatMessage(role="user", content=req.message),
    ]

    llm = _build_llm_client()
    try:
        resp = await llm.chat(messages)
    except LLMClientError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e

    reply = llm.extract_text(resp).strip()
    if not reply:
        raise HTTPException(status_code=502, detail="Empty model response.")

    latency_ms = int((time.perf_counter() - t0) * 1000)
    debug = None
    if settings.debug:
        debug = {
            "trace_id": trace_id,
            "latency_ms": latency_ms,
            "llm_request_id": resp.get("request_id"),
            "model": settings.llm_model,
        }

    return ChatResponse(reply=reply, trace_id=trace_id, debug=debug)

