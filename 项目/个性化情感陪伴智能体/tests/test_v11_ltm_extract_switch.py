"""V1.1：LTM 抽取总开关（settings + /health 可观测）。"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.core import settings as core_settings
from app.main import app


def test_health_reflects_ltm_extract_disabled(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", False)
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["ltm_extract_enabled"] is False


def test_health_reflects_ltm_extract_enabled(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    r = TestClient(app).get("/health")
    assert r.status_code == 200
    assert r.json()["ltm_extract_enabled"] is True
