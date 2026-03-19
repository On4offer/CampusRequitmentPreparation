"""
Day4 情绪识别与安全模式：trace 中可见 emotion、risk_tier；高风险时 safety_mode=True。
"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        return {
            "request_id": "test-req-id",
            "raw": {"choices": [{"message": {"content": "好的，我在这里。"}}]},
        }

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def _setup_client(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    return TestClient(app)


def test_trace_contains_emotion_and_risk_tier(monkeypatch):
    """普通输入（如焦虑）：trace.decision.emotion 含 label、intensity、evidence、risk_tier。"""
    c = _setup_client(monkeypatch)
    r = c.post("/chat", json={"message": "今天有点焦虑", "user_id": "u1", "session_id": "s1"})
    assert r.status_code == 200
    tid = r.json()["trace_id"]
    t = c.get(f"/trace/{tid}").json()
    assert "decision" in t
    emotion = t["decision"].get("emotion")
    assert emotion is not None
    assert "label" in emotion
    assert "intensity" in emotion
    assert "evidence" in emotion
    assert "risk_tier" in emotion
    assert emotion["label"] == "焦虑"
    assert emotion["risk_tier"] in ("一般", "关注", "高风险")


def test_safety_mode_triggered_for_high_risk(monkeypatch):
    """高风险输入（自伤相关）：trace.decision.safety_mode=True，safety_trigger_reason 有值。"""
    c = _setup_client(monkeypatch)
    r = c.post("/chat", json={"message": "我不想活了", "user_id": "u2", "session_id": "s2"})
    assert r.status_code == 200
    tid = r.json()["trace_id"]
    t = c.get(f"/trace/{tid}").json()
    assert t["decision"].get("safety_mode") is True
    assert t["decision"].get("safety_trigger_reason")
    assert t["decision"]["emotion"]["risk_tier"] == "高风险"
