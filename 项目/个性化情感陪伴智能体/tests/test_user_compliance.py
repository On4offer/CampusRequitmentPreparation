"""二期合规：用户维度导出与遗忘（LTM 软删 + STM 清空）。"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.llm.client import ChatMessage
from app.memory.ltm import LTMItem, ltm_store
from app.memory.store import session_store


def test_user_export_json_contains_ltm_stm_feedback(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "adm-c")
    fb = tmp_path / "fb.jsonl"
    fb.write_text(
        json.dumps({"id": "1", "user_id": "exp_u", "trace_id": "t1", "rating": "like", "timestamp_ms": 1}, ensure_ascii=False)
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(core_settings.settings, "feedback_log_path", str(fb))

    now = 99_000
    ltm_store.put(
        "exp_u",
        LTMItem(
            user_id="exp_u",
            type="Preference",
            content="喜欢猫",
            created_at=now,
            source="test",
        ),
    )
    session_store.append(user_id="exp_u", session_id="sx", message=ChatMessage(role="user", content="hi"))
    session_store.append(user_id="exp_u", session_id="sx", message=ChatMessage(role="assistant", content="hey"))

    client = TestClient(app)
    r = client.get("/users/exp_u/export", headers={"X-Admin-Token": "adm-c"})
    assert r.status_code == 200
    assert "attachment" in r.headers.get("content-disposition", "")
    data = r.json()
    assert data["user_id"] == "exp_u"
    assert data["export_version"] == 1
    assert len(data["ltm"]) >= 1
    assert any("喜欢猫" in str(x.get("content", "")) for x in data["ltm"])
    assert len(data["stm_sessions"]) >= 1
    assert len(data["feedback"]) == 1


def test_user_forget_requires_confirm(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "adm-f")
    client = TestClient(app)
    r = client.post("/users/f_u/forget", headers={"X-Admin-Token": "adm-f"}, json={"confirm": False})
    assert r.status_code == 400


def test_user_forget_soft_deletes_ltm_and_clears_stm(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "adm-f2")
    now = 100_000
    lid = ltm_store.put(
        "f_u2",
        LTMItem(
            user_id="f_u2",
            type="Event",
            content="事件",
            created_at=now,
            source="test",
        ),
    )
    session_store.append(user_id="f_u2", session_id="s1", message=ChatMessage(role="user", content="a"))

    client = TestClient(app)
    r = client.post(
        "/users/f_u2/forget",
        headers={"X-Admin-Token": "adm-f2"},
        json={"confirm": True, "clear_stm": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["ltm_deactivated"] == 1
    assert body["stm_sessions_cleared"] == 1

    item = ltm_store.get_by_id(lid)
    assert item is not None
    assert item.is_active is False
    assert session_store.get_messages(user_id="f_u2", session_id="s1") is None


def test_user_forget_without_clear_stm(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "adm-f3")
    now = 101_000
    ltm_store.put(
        "f_u3",
        LTMItem(user_id="f_u3", type="Profile", content="p", created_at=now, source="t"),
    )
    session_store.append(user_id="f_u3", session_id="s2", message=ChatMessage(role="user", content="x"))

    client = TestClient(app)
    r = client.post(
        "/users/f_u3/forget",
        headers={"X-Admin-Token": "adm-f3"},
        json={"confirm": True, "clear_stm": False},
    )
    assert r.status_code == 200
    assert r.json()["stm_sessions_cleared"] == 0
    assert session_store.get_messages(user_id="f_u3", session_id="s2") is not None
