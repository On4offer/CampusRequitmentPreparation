"""二期 Eval Lab：/admin/eval/run 与任务状态。"""

from __future__ import annotations

import time

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.core import settings as core_settings
from app.main import create_app


class _FakeLLM:
    async def chat(self, messages, *, temperature: float = 0.7):  # noqa: ANN001
        return {"request_id": "fake", "raw": {"choices": [{"message": {"content": "ok"}}]}}

    @staticmethod
    def extract_text(resp: dict) -> str:
        return str(resp["raw"]["choices"][0]["message"]["content"])


@pytest.fixture()
def eval_client(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr(core_settings.settings, "admin_config_token", "eval-adm")
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_eval_run_builtin_and_poll(eval_client: TestClient):
    h = {"X-Admin-Token": "eval-adm"}
    r = eval_client.post(
        "/admin/eval/run",
        json={"dataset": "builtin", "user_id": "eval_u1", "limit": 3},
        headers=h,
    )
    assert r.status_code == 200
    body = r.json()
    jid = body["job_id"]
    assert body["total"] == 3

    final = None
    for _ in range(120):
        s = eval_client.get(f"/admin/eval/jobs/{jid}", headers=h)
        assert s.status_code == 200
        final = s.json()
        if final["status"] in ("done", "failed"):
            break
        time.sleep(0.02)

    assert final is not None
    assert final["status"] == "done"
    assert final["summary"]["success"] == 3
    assert len(final["results"]) == 3


def test_eval_run_upload_invalid_jsonl(eval_client: TestClient):
    h = {"X-Admin-Token": "eval-adm"}
    r = eval_client.post(
        "/admin/eval/run",
        json={"dataset": "upload", "jsonl": "{not json\n"},
        headers=h,
    )
    assert r.status_code == 400
