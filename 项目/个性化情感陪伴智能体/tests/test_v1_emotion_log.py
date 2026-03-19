"""
V1 情绪落盘占位：开启时 /chat 后向 JSONL 追加一条情绪记录。
"""

from __future__ import annotations

import asyncio
import json

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as app_settings
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_emotion_log_appends_when_enabled(monkeypatch, tmp_path):
    """开启 emotion_log_enabled 且指定路径后，/chat 成功会追加一条 JSONL。"""
    import app.api.routes as routes

    log_file = tmp_path / "emotion_log.jsonl"
    monkeypatch.setattr(app_settings.settings, "emotion_log_enabled", True)
    monkeypatch.setattr(app_settings.settings, "emotion_log_path", str(log_file))
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "今天有点累", "user_id": "u1", "session_id": "s1"})
    assert r.status_code == 200
    assert log_file.exists()
    lines = log_file.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 1
    record = json.loads(lines[0])
    assert record.get("user_id") == "u1"
    assert record.get("session_id") == "s1"
    assert "timestamp_ms" in record
    assert record.get("label") is not None
    assert "intensity" in record
    assert record.get("risk_tier") is not None
    assert record.get("trace_id") == r.json().get("trace_id")
