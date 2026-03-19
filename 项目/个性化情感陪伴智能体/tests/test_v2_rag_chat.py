"""
V2 /chat 接入 RAG：开启 rag_enabled 时检索 LTM、注入证据、返回 citations、trace 含 memory_hits。
"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        content = getattr(messages[0], "content", None) or "" if messages else ""
        if "情绪识别" in content:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
        if "长期记忆" in content:
            return {
                "request_id": "c",
                "raw": {"choices": [{"message": {"content": "好的，我会记住你不喜欢鸡汤，称呼你小张。"}}]},
            }
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_chat_with_rag_returns_citations_and_trace_hits(monkeypatch):
    """开启 RAG 时：先写入 LTM，再 /chat，响应含 citations，trace 含 retrieve_ltm 与 memory_hits。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_top_k", 3)
    monkeypatch.setattr(core_settings.settings, "rag_min_score", 0.0)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    # 写入一条偏好记忆
    r0 = client.post(
        "/memory/ltm",
        json={"user_id": "u_rag", "type": "Preference", "content": "不喜欢鸡汤，叫我小张"},
    )
    assert r0.status_code == 200
    mem_id = r0.json().get("id")
    assert mem_id

    r = client.post("/chat", json={"message": "最近有点烦", "user_id": "u_rag", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert "citations" in data
    assert data["citations"] is not None
    assert len(data["citations"]) >= 1
    assert data["citations"][0].get("id") == mem_id

    tr = client.get(f"/trace/{data['trace_id']}").json()
    steps_names = [s["name"] for s in tr["steps"]]
    assert "retrieve_ltm" in steps_names
    assert tr.get("decision", {}).get("memory_hits") is not None
    assert len(tr["decision"]["memory_hits"]) >= 1
