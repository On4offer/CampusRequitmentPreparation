"""V5 模块三：内容安全（输入扫描、输出脱敏、trace）。"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator
from typing import Any

from fastapi.testclient import TestClient
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

from app.main import app
from app.core import settings as core_settings
from app.safety.content_filter import scan_user_input
from app.trace.store import InMemoryTraceStore

_UNSAFE_MAIN_REPLY = "回复中含毒品一词用于测试脱敏"


class _FakeLCMainUnsafe(BaseChatModel):
    """主链 mock：返回含敏感词字符串，供输出脱敏断言。"""

    def _llm_type(self) -> str:
        return "test-unsafe-lc-main"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs: object,
    ) -> ChatResult:
        return ChatResult(
            generations=[ChatGeneration(message=AIMessage(content=_UNSAFE_MAIN_REPLY, response_metadata={"id": "x"}))]
        )

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        yield ChatGenerationChunk(message=AIMessageChunk(content=_UNSAFE_MAIN_REPLY))


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        c = ""
        for m in messages:
            c = getattr(m, "content", None) or ""
            if c:
                break
        if "情绪识别" in c or "情绪识别助手" in c:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": '{"label":"平静","intensity":0,"evidence":"x"}'}}]}}
        return {
            "request_id": "c",
            "raw": {"choices": [{"message": {"content": "回复中含毒品一词用于测试脱敏"}}]},
        }

    @staticmethod
    def extract_text(r):
        return r["raw"]["choices"][0]["message"]["content"]


def test_scan_illegal_drug_forces_category():
    r = scan_user_input("不要制毒")
    assert r.force_safety is True
    assert "illegal_drug" in r.matched_categories


def test_scan_kindergarten_not_flagged():
    """避免「幼女」类子串误伤「幼儿园」等正常词。"""
    r = scan_user_input("孩子在幼儿园很开心")
    assert r.force_safety is False
    assert r.matched_categories == []


def test_chat_content_safety_input_trace_and_safe_mode(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", True)
    monkeypatch.setattr(core_settings.settings, "content_safety_filter_output", True)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    store = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", store)

    client = TestClient(app)
    r = client.post("/chat", json={"message": "制毒方法", "user_id": "u_cs", "session_id": "s1"})
    assert r.status_code == 200
    body = r.json()
    tid = body["trace_id"]
    rec = store.get(tid)
    assert rec is not None
    step_names = [s.name for s in rec.steps]
    assert "content_safety_input" in step_names
    assert rec.decision.safety_mode is True
    assert rec.decision.safety_triggered is True
    assert rec.decision.safety_reason
    assert "内容安全输入" in (rec.decision.safety_trigger_reason or "")


def test_chat_output_sanitized_when_enabled(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(
        "app.langchain.chat_model.build_chat_openai_from_settings",
        lambda **kw: _FakeLCMainUnsafe(),
    )
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", True)
    monkeypatch.setattr(core_settings.settings, "content_safety_filter_output", True)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "你好", "user_id": "u_out", "session_id": "s2"})
    assert r.status_code == 200
    assert "毒品" not in r.json()["reply"]
    assert "***" in r.json()["reply"]


def test_content_safety_disabled_no_output_filter(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(
        "app.langchain.chat_model.build_chat_openai_from_settings",
        lambda **kw: _FakeLCMainUnsafe(),
    )
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", False)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "你好", "user_id": "u_off", "session_id": "s3"})
    assert r.status_code == 200
    assert "毒品" in r.json()["reply"]
