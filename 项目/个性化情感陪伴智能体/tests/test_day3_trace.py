from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    """用于测试的 LLM mock：避免真实网络调用。"""

    async def chat(self, messages, temperature: float = 0.7):
        # sonar 有时会提示“async 但未使用 await”，这里做一个 0-cost 的 await 占位即可。
        await asyncio.sleep(0)
        # 返回 OpenAI 风格结构（最小字段）
        return {
            "request_id": "test-req-id",
            "raw": {"choices": [{"message": {"content": "好的，我在这里。"}}]},
        }

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_chat_creates_trace_and_can_fetch(monkeypatch):
    """
    目标：
    - 调一次 /chat，会生成 trace_id
    - 可以用 /trace/{trace_id} 查到步骤与 metrics
    """

    # 1) mock 掉 LLM
    import app.api.routes as routes

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())

    # 2) 用内存 trace store 替换默认文件 store（避免测试写磁盘）
    mem_store = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem_store)

    c = TestClient(app)

    # 3) 发起 chat
    r = c.post("/chat", json={"message": "你好", "user_id": "u1", "session_id": "s1"})
    assert r.status_code == 200
    body = r.json()
    assert body["reply"]
    assert body["trace_id"]

    tid = body["trace_id"]

    # 4) 查 trace
    r2 = c.get(f"/trace/{tid}")
    assert r2.status_code == 200
    t = r2.json()
    assert t["trace_id"] == tid
    assert t["user_id"] == "u1"
    assert t["session_id"] == "s1"
    assert isinstance(t["steps"], list) and len(t["steps"]) >= 2
    assert "metrics" in t and isinstance(t["metrics"], dict)


def test_list_traces_by_session(monkeypatch):
    """
    目标：
    - 同一会话连续调用两次 /chat
    - 用 /traces?user_id=&session_id= 能列出至少两条
    """

    import app.api.routes as routes

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    mem_store = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem_store)

    c = TestClient(app)
    c.post("/chat", json={"message": "你好", "user_id": "u2", "session_id": "s2"})
    c.post("/chat", json={"message": "再聊聊", "user_id": "u2", "session_id": "s2"})

    r = c.get("/traces", params={"user_id": "u2", "session_id": "s2", "limit": 10})
    assert r.status_code == 200
    items = r.json()["items"]
    assert len(items) >= 2

