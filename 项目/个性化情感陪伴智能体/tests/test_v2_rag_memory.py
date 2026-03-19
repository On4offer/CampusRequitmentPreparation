"""
V2 回归：预加载记忆后，/chat 应产生 citations 与 trace memory_hits。
"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.store import InMemoryTraceStore

REGRESSION_FILE = Path(__file__).resolve().parents[1] / "data" / "regression_v2.jsonl"


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        content = getattr(messages[0], "content", None) or "" if messages else ""
        if "情绪识别" in content:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的，我记住了。"}}]}}

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def _load_cases() -> list[dict]:
    if not REGRESSION_FILE.exists():
        return []
    cases = []
    for line in REGRESSION_FILE.read_text(encoding="utf-8").strip().splitlines():
        line = line.strip()
        if not line:
            continue
        cases.append(json.loads(line))
    return cases


def test_regression_v2_memory_hit_and_citations(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_top_k", 3)
    monkeypatch.setattr(core_settings.settings, "rag_min_score", 0.0)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    client = TestClient(app)

    for idx, case in enumerate(_load_cases()):
        user_id = f"v2_reg_u_{idx}"
        session_id = f"v2_reg_s_{idx}"

        for m in case.get("preload_memories", []):
            r0 = client.post(
                "/memory/ltm",
                json={
                    "user_id": user_id,
                    "type": m["type"],
                    "content": m["content"],
                },
            )
            assert r0.status_code == 200

        r = client.post(
            "/chat",
            json={"message": case.get("message", ""), "user_id": user_id, "session_id": session_id},
        )
        assert r.status_code == 200
        body = r.json()

        min_hits = int(case.get("expect_memory_hit_min", 0))
        citations = body.get("citations") or []
        assert len(citations) >= min_hits

        expect_type = case.get("expect_citation_type")
        if expect_type:
            assert any(x.get("type") == expect_type for x in citations)

        expect_reply = case.get("expect_reply_contains")
        if expect_reply:
            assert expect_reply in (body.get("reply") or "")

        tr = client.get(f"/trace/{body['trace_id']}").json()
        memory_hits = (tr.get("decision") or {}).get("memory_hits") or []
        assert len(memory_hits) >= min_hits
