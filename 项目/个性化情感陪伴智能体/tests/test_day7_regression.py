"""
Day7 回归：用 data/regression_v0.jsonl 做情绪/模式/风险稳定性校验。

约定：mock LLM 的情绪调用返回非 JSON，走规则兜底，保证同输入同输出。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.trace.store import InMemoryTraceStore

REGRESSION_FILE = Path(__file__).resolve().parents[1] / "data" / "regression_v0.jsonl"


class _FakeLLM:
    """情绪调用返回无效内容走规则；对话调用返回固定回复。"""

    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        # 若为情绪识别（system 含「情绪识别」），返回非 JSON 以触发规则兜底
        content = getattr(messages[0], "content", None) or "" if messages else ""
        if "情绪识别" in content:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
        return {
            "request_id": "c",
            "raw": {"choices": [{"message": {"content": "好的。"}}]},
        }

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def _load_cases():
    if not REGRESSION_FILE.exists():
        return []
    cases = []
    for line in REGRESSION_FILE.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        cases.append(json.loads(line))
    return cases


def test_regression_v0_stability(monkeypatch):
    """每条 regression_v0.jsonl 用例：同输入得到预期 risk_tier / mode / emotion_label。"""
    import app.api.routes as routes

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    client = TestClient(app)

    for idx, case in enumerate(_load_cases()):
        message = case.get("message", "")
        expect_risk = case.get("expect_risk_tier")
        expect_mode = case.get("expect_mode")
        expect_emotion = case.get("expect_emotion_label")

        r = client.post("/chat", json={"message": message, "user_id": "r", "session_id": "s"})
        assert r.status_code == 200, f"message={message!r} -> {r.status_code}"
        trace_id = r.json().get("trace_id")
        assert trace_id, f"message={message!r} missing trace_id"

        tr = client.get(f"/trace/{trace_id}").json()
        decision = tr.get("decision") or {}
        emotion = decision.get("emotion") or {}

        if expect_risk is not None:
            got = emotion.get("risk_tier")
            assert got == expect_risk, f"case[{idx}] risk_tier: got {got!r} expect {expect_risk!r}"
        if expect_mode is not None:
            got = decision.get("mode")
            assert got == expect_mode, f"case[{idx}] mode: got {got!r} expect {expect_mode!r}"
        if expect_emotion is not None:
            got = emotion.get("label")
            assert got == expect_emotion, f"case[{idx}] emotion label: got {got!r} expect {expect_emotion!r}"
