"""
V1 长期记忆（LTM）占位：POST/GET /memory/ltm 写入并查询。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app


def test_ltm_write_and_list():
    """POST 写入一条 LTM，GET 能按 user_id 查出。"""
    # 使用独立 store 避免与其他测试串数据；本测试直接依赖全局 ltm_store（单测顺序不确定时可用 monkeypatch 清空）
    client = TestClient(app)
    r = client.post(
        "/memory/ltm",
        json={
            "user_id": "ltm_test_user",
            "type": "Preference",
            "content": "不喜欢鸡汤",
            "source": "dialogue",
            "confidence": 0.9,
            "tags": ["风格"],
        },
    )
    assert r.status_code == 200
    data = r.json()
    assert "id" in data
    lid = data["id"]

    r2 = client.get("/memory/ltm", params={"user_id": "ltm_test_user", "limit": 10})
    assert r2.status_code == 200
    items = r2.json()["items"]
    assert len(items) >= 1
    found = next((x for x in items if x["id"] == lid), None)
    assert found is not None
    assert found["type"] == "Preference"
    assert found["content"] == "不喜欢鸡汤"
    assert found["user_id"] == "ltm_test_user"
    assert found["confidence"] == 0.9
    assert "created_at" in found


def test_ltm_list_filter_by_type():
    """GET 带 type 参数只返回该类型。"""
    client = TestClient(app)
    client.post(
        "/memory/ltm",
        json={"user_id": "ltm_filter_user", "type": "Event", "content": "上周面试了"},
    )
    client.post(
        "/memory/ltm",
        json={"user_id": "ltm_filter_user", "type": "Preference", "content": "叫我小张"},
    )
    r = client.get("/memory/ltm", params={"user_id": "ltm_filter_user", "type": "Event", "limit": 5})
    assert r.status_code == 200
    for x in r.json()["items"]:
        assert x["type"] == "Event"
