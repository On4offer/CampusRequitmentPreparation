"""
V5 模块一：用户隔离（trace/LTM 带 user_id 校验、GET /profile）。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.models import TraceDecision, TraceMetrics, TraceRecord, TraceRequest, TraceStep
from app.trace.store import InMemoryTraceStore


def _minimal_trace(trace_id: str, user_id: str) -> TraceRecord:
    return TraceRecord(
        trace_id=trace_id,
        request=TraceRequest(user_id=user_id, session_id="s", message="hi", timestamp_ms=1),
        steps=[TraceStep(name="x", start_ms=0, end_ms=1)],
        decision=TraceDecision(),
        metrics=TraceMetrics(latency_ms=1),
    )


def test_trace_forbidden_when_user_id_mismatch(monkeypatch):
    """传入 user_id 与 trace 归属不一致时 403。"""
    import app.api.routes as routes

    store = InMemoryTraceStore()
    store.put(_minimal_trace("tid1", "alice"))
    monkeypatch.setattr(routes, "trace_store", store)
    monkeypatch.setattr(core_settings.settings, "strict_user_isolation", False)

    client = TestClient(app)
    r = client.get("/trace/tid1", params={"user_id": "bob"})
    assert r.status_code == 403


def test_trace_ok_when_user_id_matches(monkeypatch):
    """传入正确 user_id 可访问 trace。"""
    import app.api.routes as routes

    store = InMemoryTraceStore()
    store.put(_minimal_trace("tid2", "alice"))
    monkeypatch.setattr(routes, "trace_store", store)

    client = TestClient(app)
    r = client.get("/trace/tid2", params={"user_id": "alice"})
    assert r.status_code == 200
    assert r.json()["user_id"] == "alice"


def test_trace_ok_without_user_id_when_not_strict(monkeypatch):
    """未传 user_id 且非严格模式：仍可访问（兼容）。"""
    import app.api.routes as routes

    store = InMemoryTraceStore()
    store.put(_minimal_trace("tid3", "alice"))
    monkeypatch.setattr(routes, "trace_store", store)
    monkeypatch.setattr(core_settings.settings, "strict_user_isolation", False)

    client = TestClient(app)
    r = client.get("/trace/tid3")
    assert r.status_code == 200


def test_trace_strict_requires_user_id(monkeypatch):
    """strict_user_isolation 下必须传 user_id。"""
    import app.api.routes as routes

    store = InMemoryTraceStore()
    store.put(_minimal_trace("tid4", "alice"))
    monkeypatch.setattr(routes, "trace_store", store)
    monkeypatch.setattr(core_settings.settings, "strict_user_isolation", True)

    client = TestClient(app)
    r = client.get("/trace/tid4")
    assert r.status_code == 400
    r2 = client.get("/trace/tid4", params={"user_id": "alice"})
    assert r2.status_code == 200


def test_ltm_by_id_forbidden_cross_user(monkeypatch):
    """PATCH LTM 时 user_id 与条目归属不一致 403。"""
    import app.api.routes as routes

    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    client = TestClient(app)
    r0 = client.post("/memory/ltm", json={"user_id": "owner1", "type": "Preference", "content": "我的偏好"})
    assert r0.status_code == 200
    lid = r0.json()["id"]

    r = client.patch(
        f"/memory/ltm/{lid}",
        params={"user_id": "hacker"},
        json={"content": "篡改"},
    )
    assert r.status_code == 403


def test_profile_returns_summary(monkeypatch):
    """GET /profile/{user_id} 返回画像摘要。"""
    import app.api.routes as routes

    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    client = TestClient(app)
    client.post("/memory/ltm", json={"user_id": "p1", "type": "Preference", "content": "喜欢咖啡"})

    r = client.get("/profile/p1", params={"viewer_user_id": "p1"})
    assert r.status_code == 200
    data = r.json()
    assert data["user_id"] == "p1"
    assert data["total_memories"] >= 1
    assert "Preference" in data.get("by_type", {})


def test_profile_forbidden_wrong_viewer(monkeypatch):
    """查看他人画像时 viewer 不匹配 403。"""
    import app.api.routes as routes

    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())
    client = TestClient(app)

    r = client.get("/profile/victim", params={"viewer_user_id": "attacker"})
    assert r.status_code == 403
