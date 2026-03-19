"""
Day5 状态机：trace 中可见 mode、mode_reason；相同输入 mode 稳定。
"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.policy import decide_mode, get_system_prompt_for_mode
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


def test_trace_contains_mode_and_mode_reason(monkeypatch):
    """chat 后 trace.decision 含 mode、mode_reason。"""
    c = _setup_client(monkeypatch)
    r = c.post("/chat", json={"message": "今天有点焦虑", "user_id": "u1", "session_id": "s1"})
    assert r.status_code == 200
    t = c.get(f"/trace/{r.json()['trace_id']}").json()
    assert t["decision"].get("mode") is not None
    assert t["decision"].get("mode_reason") is not None
    assert t["decision"]["mode"] in ("闲聊", "倾听", "安慰", "工作", "工具")


def test_explicit_listen_overrides_emotion(monkeypatch):
    """显式「只想吐槽」-> mode=倾听。"""
    mode, reason, intended_tool, _ = decide_mode("别安慰我，我只想吐槽", "低落", 2)
    assert mode == "倾听"
    assert intended_tool is None
    assert "倾听" in reason or "吐槽" in reason or "显式" in reason


def test_mode_prompts_exist():
    """五类 mode（含工具）均有对应 prompt 模板。"""
    for m in ("闲聊", "倾听", "安慰", "工作", "工具"):
        p = get_system_prompt_for_mode(m)
        assert p and len(p) > 10
        assert m in p or "模式" in p
