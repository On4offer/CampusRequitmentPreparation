from __future__ import annotations

import os
from typing import Any

import asyncio
import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import create_app


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
    def __init__(self) -> None:
        self.calls: list[list[dict[str, str]]] = []

    async def chat(self, messages, *, temperature: float = 0.7) -> dict[str, Any]:  # noqa: ANN001
        # Keep this method async to match the real client interface.
        await asyncio.sleep(0)
        # record messages for assertions
        self.calls.append([{"role": m.role, "content": m.content} for m in messages])
        # Always respond with the most recent user content
        last_user = next((m["content"] for m in reversed(self.calls[-1]) if m["role"] == "user"), "")
        return {
            "request_id": "fake",
            "raw": {"choices": [{"message": {"content": f"echo:{last_user}"}}]},
        }

    @staticmethod
    def extract_text(resp: dict[str, Any]) -> str:
        return resp["raw"]["choices"][0]["message"]["content"]


@pytest.fixture()
def client_and_fake_llm(monkeypatch: pytest.MonkeyPatch):
    fake = _FakeLLM()

    # Patch the route-level builder to avoid real network calls.
    monkeypatch.setattr(routes, "_build_llm_client", lambda: fake)

    app = create_app()
    with TestClient(app) as client:
        yield client, fake


def test_session_memory_appends_history(client_and_fake_llm):
    client, fake = client_and_fake_llm

    r1 = client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "你好"})
    assert r1.status_code == 200

    r2 = client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "你还记得我刚说了什么吗？"})
    assert r2.status_code == 200

    # 每次 /chat 会先调情绪 LLM、再调对话 LLM，故 2 轮共 4 次调用
    assert len(fake.calls) == 4
    _dump_call("emotion1", fake.calls[0])
    _dump_call("chat1", fake.calls[1])
    _dump_call("emotion2", fake.calls[2])
    _dump_call("chat2", fake.calls[3])

    # 第二轮对话的 LLM 调用应带上历史（前一轮 user + assistant）
    second = fake.calls[3]
    roles = [m["role"] for m in second]
    assert roles[0] == "system"
    # history user
    assert any(m["role"] == "user" and m["content"] == "你好" for m in second)
    # history assistant (echo of first user)
    assert any(m["role"] == "assistant" and "echo:你好" in m["content"] for m in second)
    # new user at end
    assert second[-1]["role"] == "user"


def test_session_isolation(client_and_fake_llm):
    client, fake = client_and_fake_llm

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "A"})
    client.post("/chat", json={"user_id": "u1", "session_id": "s2", "message": "B"})
    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "C"})

    # 每轮 /chat = 1 次情绪 + 1 次对话，共 3 轮 -> 6 次
    assert len(fake.calls) == 6
    _dump_call("s1-A emotion", fake.calls[0])
    _dump_call("s1-A chat", fake.calls[1])
    _dump_call("s2-B emotion", fake.calls[2])
    _dump_call("s2-B chat", fake.calls[3])
    _dump_call("s1-C emotion", fake.calls[4])
    _dump_call("s1-C chat", fake.calls[5])
    third = fake.calls[5]

    # Third call is for s1; it should include history from s1 (A and echo:A), but not from s2 (B).
    assert any(m["role"] == "user" and m["content"] == "A" for m in third)
    assert any(m["role"] == "assistant" and "echo:A" in m["content"] for m in third)
    assert not any(m["role"] == "user" and m["content"] == "B" for m in third)


def test_session_reset_clears_history(client_and_fake_llm):
    client, fake = client_and_fake_llm

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "hello"})
    rr = client.post("/sessions/reset", json={"user_id": "u1", "session_id": "s1"})
    assert rr.status_code == 200
    assert rr.json()["existed"] is True

    client.post("/chat", json={"user_id": "u1", "session_id": "s1", "message": "after"})
    # 2 轮 /chat -> 4 次调用；reset 后第二轮不应带 "hello" 历史
    assert len(fake.calls) == 4
    _dump_call("before-reset emotion", fake.calls[0])
    _dump_call("before-reset chat", fake.calls[1])
    _dump_call("after-reset emotion", fake.calls[2])
    _dump_call("after-reset chat", fake.calls[3])
    second = fake.calls[3]
    # After reset, history should not include previous "hello"
    assert not any(m["role"] == "user" and m["content"] == "hello" for m in second)

