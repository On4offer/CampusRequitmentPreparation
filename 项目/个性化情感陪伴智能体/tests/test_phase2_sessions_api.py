from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.main import create_app


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch):
    class _FakeLLM:
        async def chat(self, messages, *, temperature: float = 0.7):  # noqa: ANN001
            return {"request_id": "fake", "raw": {"choices": [{"message": {"content": "ok"}}]}}

        @staticmethod
        def extract_text(resp: dict) -> str:
            return str(resp["raw"]["choices"][0]["message"]["content"])

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())

    app = create_app()
    with TestClient(app) as c:
        yield c


def test_sessions_list_and_messages_roundtrip(client: TestClient):
    r = client.get("/sessions", params={"user_id": "u_phase2"})
    assert r.status_code == 200
    assert r.json() == {"user_id": "u_phase2", "sessions": []}

    c1 = client.post("/chat", json={"user_id": "u_phase2", "session_id": "sess_a", "message": "hi"})
    assert c1.status_code == 200

    r2 = client.get("/sessions", params={"user_id": "u_phase2"})
    assert r2.status_code == 200
    body = r2.json()
    assert body["user_id"] == "u_phase2"
    assert len(body["sessions"]) == 1
    assert body["sessions"][0]["session_id"] == "sess_a"
    assert body["sessions"][0]["message_count"] == 2

    m = client.get("/sessions/sess_a/messages", params={"user_id": "u_phase2"})
    assert m.status_code == 200
    msgs = m.json()["messages"]
    assert len(msgs) == 2
    assert msgs[0]["role"] == "user"
    assert msgs[1]["role"] == "assistant"

    d = client.delete("/sessions/sess_a", params={"user_id": "u_phase2"})
    assert d.status_code == 200
    assert d.json()["existed"] is True

    m404 = client.get("/sessions/sess_a/messages", params={"user_id": "u_phase2"})
    assert m404.status_code == 404
