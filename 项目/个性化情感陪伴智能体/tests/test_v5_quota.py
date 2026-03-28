"""V5 模块二：配额与限流。"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.quota import limiter as quota_limiter
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


def test_quota_qps_returns_429(monkeypatch):
    """QPS 超限返回 429。"""
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 1.0)
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", 0)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r1 = client.post("/chat", json={"message": "你好", "user_id": "qps_u", "session_id": "s1"})
    assert r1.status_code == 200
    r2 = client.post("/chat", json={"message": "你好2", "user_id": "qps_u", "session_id": "s1"})
    assert r2.status_code == 429


def test_quota_daily_returns_429(monkeypatch):
    """日字符预算耗尽时主 LLM 前 429。"""
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 0.0)
    day_limit = 10_000
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", day_limit)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r1 = client.post("/chat", json={"message": "短", "user_id": "day_u", "session_id": "s1"})
    assert r1.status_code == 200
    # 首轮后把用量顶到「再扣一轮情绪+主 prompt 估算」必超，避免依赖 system prompt 实际长度
    quota_limiter.seed_daily_usage_for_tests("day_u", day_limit - 500)
    r2 = client.post("/chat", json={"message": "短", "user_id": "day_u", "session_id": "s1"})
    assert r2.status_code == 429
    body = r2.json()
    assert body.get("detail", {}).get("error") == "quota_exceeded"


def test_quota_disabled_no_block(monkeypatch):
    """未开启配额时不拦截。"""
    import app.api.routes as routes

    quota_limiter.reset_for_tests()
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    for _ in range(3):
        r = client.post("/chat", json={"message": "测", "user_id": "free_u", "session_id": "s1"})
        assert r.status_code == 200
