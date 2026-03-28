"""V5 模块五：运营热配置 /admin/config。"""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings


def test_admin_quota_and_risk_endpoints(monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "adm-x")
    client = TestClient(app)
    rq = client.get("/admin/quota", headers={"X-Admin-Token": "adm-x"}, params={"user_id": "quota_u"})
    assert rq.status_code == 200
    data = rq.json()
    assert data["user_id"] == "quota_u"
    assert "used_today" in data
    rr = client.get("/admin/risk_events", headers={"X-Admin-Token": "adm-x"}, params={"limit": 5})
    assert rr.status_code == 200
    assert "items" in rr.json()
    assert rr.json()["storage"] in ("file_store", "memory_store", "unknown_store")


def _restore_settings(**kwargs: object) -> None:
    for k, v in kwargs.items():
        object.__setattr__(core_settings.settings, k, v)


def test_get_admin_config_with_token(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "secret-admin")
    monkeypatch.setattr(core_settings.settings, "hot_config_path", str(tmp_path / "hc.json"))

    client = TestClient(app)
    r = client.get("/admin/config", headers={"X-Admin-Token": "wrong"})
    assert r.status_code == 401

    r2 = client.get("/admin/config", headers={"X-Admin-Token": "secret-admin"})
    assert r2.status_code == 200
    body = r2.json()
    assert "rag_top_k" in body
    assert body["rag_enabled"] is core_settings.settings.rag_enabled


def test_patch_admin_config_persists_and_updates_settings(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "t1")
    hc = tmp_path / "hc.json"
    monkeypatch.setattr(core_settings.settings, "hot_config_path", str(hc))

    old_topk = core_settings.settings.rag_top_k
    old_tool = core_settings.settings.tool_enabled
    old_ltm_en = core_settings.settings.ltm_extract_enabled
    old_ltm_n = core_settings.settings.ltm_extract_every_n_turns
    try:
        client = TestClient(app)
        r = client.patch(
            "/admin/config",
            headers={"X-Admin-Token": "t1"},
            json={"rag_top_k": 7, "tool_enabled": True},
        )
        assert r.status_code == 200
        assert r.json()["rag_top_k"] == 7
        assert r.json()["tool_enabled"] is True
        assert core_settings.settings.rag_top_k == 7
        assert core_settings.settings.tool_enabled is True
        assert hc.exists()
        assert '"rag_top_k": 7' in hc.read_text(encoding="utf-8")

        r_ltm = client.patch(
            "/admin/config",
            headers={"X-Admin-Token": "t1"},
            json={"ltm_extract_enabled": True, "ltm_extract_every_n_turns": 2},
        )
        assert r_ltm.status_code == 200
        assert r_ltm.json()["ltm_extract_enabled"] is True
        assert r_ltm.json()["ltm_extract_every_n_turns"] == 2
        assert core_settings.settings.ltm_extract_enabled is True
        assert core_settings.settings.ltm_extract_every_n_turns == 2
    finally:
        _restore_settings(
            rag_top_k=old_topk,
            tool_enabled=old_tool,
            ltm_extract_enabled=old_ltm_en,
            ltm_extract_every_n_turns=old_ltm_n,
        )


def test_patch_admin_config_validation(tmp_path: Path, monkeypatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "t2")
    monkeypatch.setattr(core_settings.settings, "hot_config_path", str(tmp_path / "hc2.json"))

    client = TestClient(app)
    r = client.patch(
        "/admin/config",
        headers={"X-Admin-Token": "t2"},
        json={"rag_top_k": 999},
    )
    assert r.status_code == 400
    assert "rag_top_k" in r.json()["detail"].lower() or "50" in r.json()["detail"]

    r2 = client.patch(
        "/admin/config",
        headers={"X-Admin-Token": "t2"},
        json={"ltm_extract_every_n_turns": 99},
    )
    assert r2.status_code == 400
    assert "ltm_extract_every_n_turns" in r2.json()["detail"].lower()


def test_load_hot_config_on_import_applies_file(tmp_path: Path, monkeypatch):
    """直接调用 load_hot_config_from_disk（与 main 启动时一致）。"""
    from app.config import hot_config as hc

    p = tmp_path / "boot.json"
    p.write_text('{"rag_top_k": 6, "quota_enabled": true}', encoding="utf-8")
    monkeypatch.setattr(core_settings.settings, "hot_config_path", str(p))

    old_topk = core_settings.settings.rag_top_k
    old_quota = core_settings.settings.quota_enabled
    try:
        applied = hc.load_hot_config_from_disk()
        assert applied.get("rag_top_k") == 6
        assert core_settings.settings.rag_top_k == 6
        assert core_settings.settings.quota_enabled is True
    finally:
        _restore_settings(rag_top_k=old_topk, quota_enabled=old_quota)
