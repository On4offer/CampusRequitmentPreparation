from __future__ import annotations

import os
from typing import Any

import asyncio
import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import create_app
from tests.orchestrator_mocks import LC_MAIN_REPLY


def _debug_enabled() -> bool:
    return os.getenv("DAY2_TEST_DEBUG", "").strip() not in {"", "0", "false", "False"}


def _dump_call(tag: str, call: list[dict[str, str]]) -> None:
    if not _debug_enabled():
        return
    print(f"\n[{tag}] messages={len(call)}")
    for i, m in enumerate(call):
        content = (m.get("content") or "").replace("\n", "\\n")
        if len(content) > 120:
            content = content[:120] + "...(truncated)"
        print(f"  {i:02d} {m.get('role')}: {content}")


class _FakeLLM:
    """仅情绪 / 隐式抽取等走 httpx LLMClient；主对话由 conftest mock 的 LangChain ChatModel 负责。"""

    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    async def chat(self, messages, *, temperature: float = 0.7) -> dict[str, Any]:  # noqa: ANN001
        await asyncio.sleep(0)
        self.calls.append([{"role": m.role, "content": m.content} for m in messages])
        return {
            "request_id": "fake",
            "raw": {"choices": [{"message": {"content": "{}"}}]},
        }

    @staticmethod
    def extract_text(resp: dict[str, Any]) -> str:
        return resp["raw"]["choices"][0]["message"]["content"]


@pytest.fixture()
def client_and_fake_llm(monkeypatch: pytest.MonkeyPatch):
    fake = _FakeLLM()
    monkeypatch.setattr(routes, "_build_llm_client", lambda: fake)
    app = create_app()
    with TestClient(app) as client:
        yield client, fake


def test_session_memory_appends_history(client_and_fake_llm):
    client, fake = client_and_fake_llm

    r1 = client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "你好"})
    assert r1.status_code == 200
    assert r1.json()["reply"] == LC_MAIN_REPLY.strip()

    r2 = client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "你还记得我刚说了什么吗？"})
    assert r2.status_code == 200
    assert r2.json()["reply"] == LC_MAIN_REPLY.strip()

    # 每轮仅情绪分析调用 httpx LLMClient
    assert len(fake.calls) == 2
    _dump_call("emotion1", fake.calls[0])
    _dump_call("emotion2", fake.calls[1])

    msgs = client.get("/sessions/s1/messages", params={"user_id": "u1"}).json()["messages"]
    roles = [m["role"] for m in msgs]
    assert "user" in roles and "assistant" in roles
    assert any(m["role"] == "user" and m["content"] == "你好" for m in msgs)
    assert any(m["role"] == "assistant" and m["content"] == LC_MAIN_REPLY.strip() for m in msgs)


def test_session_isolation(client_and_fake_llm):
    client, fake = client_and_fake_llm

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "A"})
    client.post("/chat", json={"user_id": "u1", "session_id": "s2", "message": "B"})
    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "C"})

    assert len(fake.calls) == 3

    third = fake.calls[2]
    assert any(m["role"] == "user" and m["content"] == "C" for m in third)

    s1_msgs = client.get("/sessions/s1/messages", params={"user_id": "u1"}).json()["messages"]
    assert any(m["role"] == "user" and m["content"] == "A" for m in s1_msgs)
    assert not any(m["role"] == "user" and m["content"] == "B" for m in s1_msgs)


def test_session_reset_clears_history(client_and_fake_llm):
    client, fake = client_and_fake_llm

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "hello"})
    rr = client.post("/sessions/reset", json={"user_id": "u1", "session_id": "s1"})
    assert rr.status_code == 200
    assert rr.json()["existed"] is True

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "after"})
    assert len(fake.calls) == 2
    second = fake.calls[1]
    assert not any(m["role"] == "user" and m["content"] == "hello" for m in second)
    stm = client.get("/sessions/s1/messages", params={"user_id": "u1"}).json()["messages"]
    assert not any(m["role"] == "user" and m["content"] == "hello" for m in stm)
    assert any(m["role"] == "user" and m["content"] == "after" for m in stm)
