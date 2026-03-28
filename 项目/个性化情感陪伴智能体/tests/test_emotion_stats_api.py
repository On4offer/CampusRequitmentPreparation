"""GET /emotion/stats 聚合情绪日志。"""

from __future__ import annotations

import json
import time

from fastapi.testclient import TestClient

from app.core import settings as core_settings
from app.main import app


def test_emotion_stats_empty_file(tmp_path, monkeypatch):
    log = tmp_path / "empty.jsonl"
    log.write_text("", encoding="utf-8")
    monkeypatch.setattr(core_settings.settings, "emotion_log_path", str(log))

    client = TestClient(app)
    r = client.get("/emotion/stats", params={"user_id": "u_x", "window": "week"})
    assert r.status_code == 200
    b = r.json()
    assert b["record_count"] == 0
    assert b["user_id"] == "u_x"
    assert "免责声明" in b["disclaimer"] or "诊断" in b["disclaimer"]
    assert b["hint"]


def test_emotion_stats_with_records(tmp_path, monkeypatch):
    log = tmp_path / "e.jsonl"
    now = int(time.time() * 1000)
    rows = [
        {"user_id": "stat_u", "timestamp_ms": now, "label": "平静", "risk_tier": "一般", "trace_id": "t1"},
        {"user_id": "stat_u", "timestamp_ms": now - 3600000, "label": "焦虑", "risk_tier": "关注", "trace_id": "t2"},
        {"user_id": "other", "timestamp_ms": now, "label": "开心", "risk_tier": "一般", "trace_id": "t3"},
    ]
    log.write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in rows) + "\n", encoding="utf-8")
    monkeypatch.setattr(core_settings.settings, "emotion_log_path", str(log))

    client = TestClient(app)
    r = client.get("/emotion/stats", params={"user_id": "stat_u", "window": "day"})
    assert r.status_code == 200
    b = r.json()
    assert b["record_count"] == 2
    assert b["by_label"]["平静"] == 1
    assert b["by_label"]["焦虑"] == 1
    assert b["by_risk_tier"]["关注"] == 1
    assert len(b["series"]) == 24
