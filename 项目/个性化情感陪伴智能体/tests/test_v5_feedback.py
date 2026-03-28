"""V5 模块四：反馈闭环。"""

from __future__ import annotations

import asyncio
import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.store import InMemoryTraceStore


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
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(r):
        return r["raw"]["choices"][0]["message"]["content"]


def test_post_feedback_like_persists(tmp_path: Path, monkeypatch):
    import app.api.routes as routes

    fb = tmp_path / "fb.jsonl"
    ev = tmp_path / "ev.jsonl"
    monkeypatch.setattr(core_settings.settings, "feedback_enabled", True)
    monkeypatch.setattr(core_settings.settings, "feedback_log_path", str(fb))
    monkeypatch.setattr(core_settings.settings, "feedback_eval_log_path", str(ev))
    monkeypatch.setattr(core_settings.settings, "feedback_eval_mirror_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    cr = client.post("/chat", json={"message": "测反馈", "user_id": "fb_u", "session_id": "sfb"})
    assert cr.status_code == 200
    tid = cr.json()["trace_id"]

    fr = client.post(
        "/feedback",
        json={"trace_id": tid, "user_id": "fb_u", "rating": "like"},
    )
    assert fr.status_code == 200
    body = fr.json()
    assert body["ok"] is True
    assert body["mirrored_to_eval"] is False

    assert fb.exists()
    line = fb.read_text(encoding="utf-8").strip().splitlines()[-1]
    row = json.loads(line)
    assert row["trace_id"] == tid
    assert row["rating"] == "like"
    assert row["user_id"] == "fb_u"
    assert not ev.exists() or ev.read_text(encoding="utf-8").strip() == ""


def test_post_feedback_dislike_mirrors_eval(tmp_path: Path, monkeypatch):
    import app.api.routes as routes

    fb = tmp_path / "fb.jsonl"
    ev = tmp_path / "ev.jsonl"
    monkeypatch.setattr(core_settings.settings, "feedback_enabled", True)
    monkeypatch.setattr(core_settings.settings, "feedback_log_path", str(fb))
    monkeypatch.setattr(core_settings.settings, "feedback_eval_log_path", str(ev))
    monkeypatch.setattr(core_settings.settings, "feedback_eval_mirror_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    cr = client.post("/chat", json={"message": "x", "user_id": "u2", "session_id": "s2"})
    tid = cr.json()["trace_id"]

    fr = client.post(
        "/feedback",
        json={"trace_id": tid, "user_id": "u2", "rating": "dislike", "correction": "应更共情"},
    )
    assert fr.status_code == 200
    assert fr.json()["mirrored_to_eval"] is True
    assert ev.exists()
    ev_line = json.loads(ev.read_text(encoding="utf-8").strip().splitlines()[-1])
    assert ev_line["trace_id"] == tid
    assert ev_line["correction"] == "应更共情"


def test_post_feedback_wrong_user_403(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "feedback_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    cr = client.post("/chat", json={"message": "a", "user_id": "owner", "session_id": "s"})
    tid = cr.json()["trace_id"]

    fr = client.post(
        "/feedback",
        json={"trace_id": tid, "user_id": "other", "rating": "like"},
    )
    assert fr.status_code == 403


def test_post_feedback_unknown_trace_404(monkeypatch):
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "feedback_enabled", True)
    client = TestClient(app)
    fr = client.post(
        "/feedback",
        json={"trace_id": "00000000-0000-0000-0000-000000000000", "user_id": "x", "rating": "like"},
    )
    assert fr.status_code == 404


def test_feedback_export_jsonl(tmp_path: Path, monkeypatch):
    import app.api.routes as routes

    fb = tmp_path / "fb.jsonl"
    monkeypatch.setattr(core_settings.settings, "feedback_enabled", True)
    monkeypatch.setattr(core_settings.settings, "feedback_log_path", str(fb))
    monkeypatch.setattr(core_settings.settings, "quota_enabled", False)
    monkeypatch.setattr(core_settings.settings, "content_safety_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    cr = client.post("/chat", json={"message": "e", "user_id": "eu", "session_id": "se"})
    tid = cr.json()["trace_id"]
    client.post("/feedback", json={"trace_id": tid, "user_id": "eu", "rating": "like"})

    er = client.get("/feedback/export", params={"limit": 10})
    assert er.status_code == 200
    data = er.json()
    assert data["line_count"] >= 1
    assert tid in data["content"]
