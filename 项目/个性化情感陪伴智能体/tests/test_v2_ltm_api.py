"""
V2 模块一/五：LTM 查询增强（q、按 id）与更新/软删除。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_ltm_get_by_id_and_query_and_soft_delete():
    client = TestClient(app)
    user_id = "v2_ltm_api_user"

    r0 = client.post(
        "/memory/ltm",
        json={"user_id": user_id, "type": "Preference", "content": "不喜欢鸡汤，回答直接一点"},
    )
    assert r0.status_code == 200
    lid = r0.json()["id"]

    r1 = client.get(f"/memory/ltm/{lid}")
    assert r1.status_code == 200
    item = r1.json()
    assert item["id"] == lid
    assert item["is_active"] is True

    r2 = client.get("/memory/ltm", params={"user_id": user_id, "q": "鸡汤"})
    assert r2.status_code == 200
    ids = {x["id"] for x in r2.json()["items"]}
    assert lid in ids

    r3 = client.patch(f"/memory/ltm/{lid}", json={"content": "不要鸡汤，尽量简洁", "confidence": 0.8})
    assert r3.status_code == 200
    assert abs(float(r3.json()["confidence"]) - 0.8) < 1e-6
    assert "不要鸡汤" in r3.json()["content"]

    r4 = client.delete(f"/memory/ltm/{lid}")
    assert r4.status_code == 200
    assert r4.json()["ok"] is True

    r5 = client.get(f"/memory/ltm/{lid}")
    assert r5.status_code == 404
