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

    async def chat_stream(self, messages, temperature: float = 0.7, meta_out=None):
        await asyncio.sleep(0)
        if meta_out is not None:
            meta_out["request_id"] = "stream-test-id"
        text = _FakeLLM.extract_text(await self.chat(messages, temperature=temperature))
        yield text

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


def test_chat_stream_sse_done(monkeypatch):
    """POST /chat/stream 返回 SSE，末包 event=done 含 reply/trace_id。"""
    import app.api.routes as routes

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    mem_store = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem_store)

    c = TestClient(app)
    with c.stream(
        "POST",
        "/chat/stream",
        json={"message": "流式你好", "user_id": "u_stream", "session_id": "s_stream"},
    ) as r:
        assert r.status_code == 200
        raw = b"".join(r.iter_bytes()).decode("utf-8")
    assert "event" in raw or "meta" in raw
    assert '"event": "done"' in raw or '"done"' in raw
    assert "trace_id" in raw
    assert "好的，我在这里" in raw


def test_list_traces_requires_non_empty_session_id():
    """GET /traces 省略或空 session_id 时返回 400，避免误用随机 UUID 静默空列表。"""
    c = TestClient(app)
    r = c.get("/traces", params={"limit": 5})
    assert r.status_code == 400
    assert "session_id" in (r.json().get("detail") or "").lower()

    r2 = c.get("/traces", params={"user_id": "u1", "session_id": "", "limit": 5})
    assert r2.status_code == 400

    r3 = c.get("/traces", params={"user_id": "u1", "session_id": "   ", "limit": 5})
    assert r3.status_code == 400

