"""二期：日配额触顶时的「省流降级」（去 RAG + 短提示）。"""

from __future__ import annotations

import asyncio

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.memory.ltm import LTMItem
from app.quota import limiter as quota_limiter
from app.rag.retriever import RetrievedMemory
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        c = ""
        for m in messages:
            c = getattr(m, "content", None) or ""
            if c:
                break
        if "情绪识别" in c:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(r):
        return r["raw"]["choices"][0]["message"]["content"]


def _big_rag_retrieve(*, user_id: str, query: str, **kwargs) -> list[RetrievedMemory]:
    item = LTMItem(
        id="big-m",
        user_id=user_id,
        type="Event",
        content="x" * 7000,
        created_at=1,
        source="test",
    )
    return [RetrievedMemory(item=item, score=0.99)]


def test_quota_degrade_strips_rag_and_succeeds(monkeypatch):
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 0.0)
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", 5000)
    monkeypatch.setattr(core_settings.settings, "quota_degrade_on_exhaust", True)
    monkeypatch.setattr(core_settings.settings, "quota_degrade_system_hint", "")
    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_max_chars", 20_000)
    monkeypatch.setattr(core_settings.settings, "rag_rewrite_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    monkeypatch.setattr(routes.ltm_retriever, "retrieve", _big_rag_retrieve)

    client = TestClient(app)
    r = client.post("/chat", json={"message": "hi", "user_id": "deg_u1", "session_id": "s1"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("quota_degraded") is True
    assert body.get("citations") is None
    tid = body["trace_id"]
    tr = client.get(f"/trace/{tid}", params={"user_id": "deg_u1"})
    assert tr.status_code == 200
    rec = tr.json()
    dec = rec["decision"]
    assert dec.get("quota_exceeded") is True
    assert dec.get("degraded_mode") is True
    assert any(s["name"] == "quota_degraded" for s in rec["steps"])


def test_quota_degrade_off_still_429(monkeypatch):
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 0.0)
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", 5000)
    monkeypatch.setattr(core_settings.settings, "quota_degrade_on_exhaust", False)
    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_max_chars", 20_000)
    monkeypatch.setattr(core_settings.settings, "rag_rewrite_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    monkeypatch.setattr(routes.ltm_retriever, "retrieve", _big_rag_retrieve)

    client = TestClient(app)
    r = client.post("/chat", json={"message": "hi", "user_id": "deg_u2", "session_id": "s1"})
    assert r.status_code == 429


def test_quota_degrade_still_429_when_budget_too_tight(monkeypatch):
    """去掉 RAG 后仍超日预算 → 429。"""
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 0.0)
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", 400)
    monkeypatch.setattr(core_settings.settings, "quota_degrade_on_exhaust", True)
    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_max_chars", 20_000)
    monkeypatch.setattr(core_settings.settings, "rag_rewrite_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    monkeypatch.setattr(routes.ltm_retriever, "retrieve", _big_rag_retrieve)

    client = TestClient(app)
    r = client.post("/chat", json={"message": "hi", "user_id": "deg_u3", "session_id": "s1"})
    assert r.status_code == 429
