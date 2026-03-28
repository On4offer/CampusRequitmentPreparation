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


def test_ltm_list_pagination_and_total():
    client = TestClient(app)
    user_id = "v2_ltm_page_user"
    for i in range(3):
        r = client.post(
            "/memory/ltm",
            json={"user_id": user_id, "type": "Profile", "content": f"条目{i}"},
        )
        assert r.status_code == 200

    p0 = client.get("/memory/ltm", params={"user_id": user_id, "limit": 2, "offset": 0})
    assert p0.status_code == 200
    b0 = p0.json()
    assert b0["total"] == 3
    assert len(b0["items"]) == 2
    assert b0["offset"] == 0
    assert b0["limit"] == 2

    p1 = client.get("/memory/ltm", params={"user_id": user_id, "limit": 2, "offset": 2})
    assert p1.status_code == 200
    b1 = p1.json()
    assert b1["total"] == 3
    assert len(b1["items"]) == 1


def test_ltm_list_filter_by_source():
    client = TestClient(app)
    user_id = "v2_ltm_src_user"

    r_a = client.post(
        "/memory/ltm",
        json={
            "user_id": user_id,
            "type": "Preference",
            "content": "手写一条",
            "source": "manual_test",
        },
    )
    assert r_a.status_code == 200
    r_b = client.post(
        "/memory/ltm",
        json={
            "user_id": user_id,
            "type": "Event",
            "content": "隐式风格",
            "source": "dialogue_extract",
        },
    )
    assert r_b.status_code == 200

    all_rows = client.get("/memory/ltm", params={"user_id": user_id})
    assert all_rows.json()["total"] == 2

    only_dx = client.get("/memory/ltm", params={"user_id": user_id, "source": "dialogue_extract"})
    assert only_dx.json()["total"] == 1
    assert only_dx.json()["items"][0]["source"] == "dialogue_extract"

    only_m = client.get("/memory/ltm", params={"user_id": user_id, "source": "manual_test"})
    assert only_m.json()["total"] == 1
    assert only_m.json()["items"][0]["source"] == "manual_test"
