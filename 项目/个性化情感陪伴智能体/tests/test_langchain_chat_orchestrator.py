"""
核心对话路径：主回复走 LangChain LCEL；单测由 conftest mock ChatOpenAI，此处只 patch 自研 LLMClient（与情绪等对齐）。
"""

from __future__ import annotations

import asyncio

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.trace.store import InMemoryTraceStore
from tests.orchestrator_mocks import FakeLCMainChatModel, LC_MAIN_REPLY, patch_llm_client

CHAT_REPLY = LC_MAIN_REPLY


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        return {
            "request_id": "test-req-id",
            "raw": {"choices": [{"message": {"content": CHAT_REPLY}}]},
        }

    async def chat_stream(self, messages, temperature: float = 0.7, meta_out=None):
        await asyncio.sleep(0)
        if meta_out is not None:
            meta_out["request_id"] = "stream-test-id"
        yield CHAT_REPLY

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_build_main_chat_lc_chain_invokes():
    from app.langchain.llm_trace_callback import LlmProviderIdCallback
    from app.langchain.main_chain import build_main_chat_lc_chain
    from app.langchain.messages import chat_messages_to_lc
    from app.llm.client import ChatMessage

    async def _run():
        chain = build_main_chat_lc_chain(FakeLCMainChatModel())
        lc = chat_messages_to_lc(
            [ChatMessage(role="system", content="s"), ChatMessage(role="user", content="u")]
        )
        sink: dict[str, str | None] = {}
        text = await chain.ainvoke({"messages": lc}, config={"callbacks": [LlmProviderIdCallback(sink)]})
        assert text == CHAT_REPLY
        assert sink.get("request_id") == "lc-json-id"

    asyncio.run(_run())


def test_chat_json_reply(monkeypatch):
    import app.api.routes as routes

    patch_llm_client(monkeypatch, _FakeLLM())

    mem = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem)

    c = TestClient(app)
    r = c.post("/chat", json={"message": "你好", "user_id": "orch_u", "session_id": "orch_s"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reply"] == CHAT_REPLY.strip()
    assert body["trace_id"]

    tr = c.get(f"/trace/{body['trace_id']}").json()
    step_names = [s["name"] for s in tr["steps"]]
    assert "llm_call" in step_names


def test_chat_stream_done_contains_reply(monkeypatch):
    import app.api.routes as routes

    patch_llm_client(monkeypatch, _FakeLLM())

    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    c = TestClient(app)
    with c.stream(
        "POST",
        "/chat/stream",
        json={"message": "流式", "user_id": "orch_us", "session_id": "orch_ss"},
    ) as r:
        assert r.status_code == 200
        raw = b"".join(r.iter_bytes()).decode("utf-8")
    assert CHAT_REPLY.strip() in raw.replace(" ", "")
    assert '"event": "done"' in raw or "done" in raw
