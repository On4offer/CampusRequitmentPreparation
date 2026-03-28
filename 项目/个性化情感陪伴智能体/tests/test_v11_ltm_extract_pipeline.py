"""V1.1：隐式 LTM 抽取管线（开关、每 N 轮触发、失败隔离、Trace）。"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient

import app.api.routes as routes
from app.core import settings as core_settings
from app.main import app
from app.trace.store import InMemoryTraceStore
from tests.orchestrator_mocks import patch_llm_client as _patch_llm_client

_EMOTION_JSON = '{"label":"平静","intensity":1,"evidence":"测"}'


def _wrap(content: str) -> dict[str, Any]:
    return {"request_id": "fake", "raw": {"choices": [{"message": {"content": content}}]}}


class _FakeLLMExtract:
    """情绪 / 主对话 / 抽取 三分支。"""

    def __init__(self, *, extract_body: str | None = None) -> None:
        self.calls: list[str] = []
        self._extract_body = extract_body

    async def chat(self, messages, temperature: float = 0.7):  # noqa: ANN001
        await asyncio.sleep(0)
        sys_c = (messages[0].content or "") if messages else ""
        self.calls.append(sys_c[:80])
        if "长期记忆抽取助手" in sys_c:
            body = self._extract_body
            if body is None:
                body = (
                    '{"items":[{"type":"Preference","content":"用户不吃辣","confidence":0.9,"tags":["饮食"]}]}'
                )
            return _wrap(body)
        if "情绪识别助手" in sys_c:
            return _wrap(_EMOTION_JSON)
        last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
        return _wrap(f"echo:{last_user}")

    @staticmethod
    def extract_text(chat_response: dict[str, Any]) -> str:
        return chat_response["raw"]["choices"][0]["message"]["content"]


@pytest.fixture()
def trace_mem(monkeypatch: pytest.MonkeyPatch):
    mem = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem)
    return mem


def test_ltm_extract_off_no_extra_llm_no_write(monkeypatch, trace_mem):
    _patch_llm_client(monkeypatch, _FakeLLMExtract())
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", False)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    uid = f"u_off_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r = c.post("/chat", json={"message": "我不吃辣", "user_id": uid, "session_id": "s1"})
    assert r.status_code == 200
    assert r.json().get("ltm_extract_written", 0) == 0

    lr = c.get("/memory/ltm", params={"user_id": uid, "limit": 50})
    assert lr.status_code == 200
    assert lr.json()["total"] == 0


def test_ltm_extract_on_writes_and_trace(monkeypatch, trace_mem):
    fake = _FakeLLMExtract()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    uid = f"u_on_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r = c.post("/chat", json={"message": "我不吃辣", "user_id": uid, "session_id": "s1"})
    assert r.status_code == 200
    assert r.json()["ltm_extract_written"] == 1
    assert any("长期记忆抽取助手" in x for x in fake.calls)

    lr = c.get("/memory/ltm", params={"user_id": uid, "limit": 50})
    assert lr.status_code == 200
    assert lr.json()["total"] >= 1
    row = next(x for x in lr.json()["items"] if x.get("source") == "dialogue_extract")
    assert "辣" in row["content"]

    tid = r.json()["trace_id"]
    tr = c.get(f"/trace/{tid}")
    assert tr.status_code == 200
    names = [s["name"] for s in tr.json()["steps"]]
    assert "ltm_extract" in names
    assert tr.json()["decision"].get("ltm_extract_written") == 1
    assert tr.json()["decision"].get("ltm_extract_updated", 0) == 0
    new_ids = tr.json()["decision"].get("ltm_extract_new_ids") or []
    assert len(new_ids) == 1
    assert r.json().get("ltm_extract_new_ids") == new_ids


def test_ltm_undo_extract_soft_deletes(monkeypatch, trace_mem):
    fake = _FakeLLMExtract()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    uid = f"u_undo_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r = c.post("/chat", json={"message": "我不吃辣", "user_id": uid, "session_id": "su"})
    assert r.status_code == 200
    tid = r.json()["trace_id"]
    ids = r.json().get("ltm_extract_new_ids") or []
    assert len(ids) == 1

    assert c.get("/memory/ltm", params={"user_id": uid, "limit": 20}).json()["total"] >= 1

    u = c.post("/memory/ltm/undo_extract", json={"trace_id": tid, "user_id": uid})
    assert u.status_code == 200
    assert u.json()["deactivated"] == 1

    lr = c.get("/memory/ltm", params={"user_id": uid, "limit": 20})
    assert lr.json()["total"] == 0

    u2 = c.post("/memory/ltm/undo_extract", json={"trace_id": tid, "user_id": uid})
    assert u2.json()["deactivated"] == 0


def test_ltm_extract_dedup_skip_second_round(monkeypatch, trace_mem):
    fake = _FakeLLMExtract()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    uid = f"u_dedup_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r1 = c.post("/chat", json={"message": "我不吃辣", "user_id": uid, "session_id": "sd"})
    assert r1.status_code == 200
    assert r1.json()["ltm_extract_written"] == 1

    r2 = c.post("/chat", json={"message": "再说一下口味", "user_id": uid, "session_id": "sd"})
    assert r2.status_code == 200
    assert r2.json()["ltm_extract_written"] == 0
    assert r2.json().get("ltm_extract_updated", 0) == 0

    lr = c.get("/memory/ltm", params={"user_id": uid, "limit": 50})
    assert lr.json()["total"] == 1

    step = next(s for s in c.get(f"/trace/{r2.json()['trace_id']}").json()["steps"] if s["name"] == "ltm_extract")
    assert "skipped_dup=1" in (step.get("output_summary") or "")


def test_ltm_extract_dedup_merge_updates(monkeypatch, trace_mem):
    """相似度在 merge 区间时合并更新同一行，不新增。"""

    class _FakeMerge(_FakeLLMExtract):
        def __init__(self) -> None:
            super().__init__()
            self._ext_i = 0

        async def chat(self, messages, temperature: float = 0.7):  # noqa: ANN001
            await asyncio.sleep(0)
            sys_c = (messages[0].content or "") if messages else ""
            self.calls.append(sys_c[:80])
            if "长期记忆抽取助手" in sys_c:
                self._ext_i += 1
                if self._ext_i == 1:
                    body = '{"items":[{"type":"Preference","content":"用户不吃辣","confidence":0.9,"tags":["饮食"]}]}'
                else:
                    body = '{"items":[{"type":"Preference","content":"用户完全不吃辣","confidence":0.9,"tags":["辣"]}]}'
                return _wrap(body)
            if "情绪识别助手" in sys_c:
                return _wrap(_EMOTION_JSON)
            last_user = next((m.content for m in reversed(messages) if m.role == "user"), "")
            return _wrap(f"echo:{last_user}")

    fake = _FakeMerge()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    uid = f"u_merge_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r1 = c.post("/chat", json={"message": "口味", "user_id": uid, "session_id": "sm"})
    assert r1.status_code == 200
    assert r1.json()["ltm_extract_written"] == 1

    r2 = c.post("/chat", json={"message": "补充口味", "user_id": uid, "session_id": "sm"})
    assert r2.status_code == 200
    assert r2.json()["ltm_extract_written"] == 0
    assert r2.json().get("ltm_extract_updated", 0) == 1

    lr = c.get("/memory/ltm", params={"user_id": uid, "limit": 50})
    assert lr.json()["total"] == 1
    assert "完全" in lr.json()["items"][0]["content"]


def test_ltm_extract_skipped_safety_mode(monkeypatch, trace_mem):
    fake = _FakeLLMExtract()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    c = TestClient(app)
    r = c.post(
        "/chat",
        json={"message": "我想自杀", "user_id": f"u_hi_{uuid.uuid4().hex[:8]}", "session_id": "s1"},
    )
    assert r.status_code == 200
    assert r.json().get("ltm_extract_written", 0) == 0
    assert not any("长期记忆抽取助手" in x for x in fake.calls)

    steps = c.get(f"/trace/{r.json()['trace_id']}").json()["steps"]
    lt = [s for s in steps if s["name"] == "ltm_extract"]
    assert lt and "safety" in (lt[0].get("output_summary") or "")


def test_ltm_extract_parse_fail_isolated(monkeypatch, trace_mem):
    fake = _FakeLLMExtract(extract_body="NOT_JSON_AT_ALL")
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)

    c = TestClient(app)
    r = c.post("/chat", json={"message": "随便聊聊", "user_id": f"u_bad_{uuid.uuid4().hex[:8]}", "session_id": "s1"})
    assert r.status_code == 200
    assert r.json().get("ltm_extract_written", 0) == 0

    steps = c.get(f"/trace/{r.json()['trace_id']}").json()["steps"]
    lt = [s for s in steps if s["name"] == "ltm_extract"]
    assert lt and lt[0].get("error")


def test_ltm_extract_skipped_when_quota_pre_check_fails(monkeypatch, trace_mem):
    """日配额下抽取前预检失败则不调抽取 LLM（主对话仍成功）。"""
    import app.memory.ltm_extract as ltm_ex

    _patch_llm_client(monkeypatch, _FakeLLMExtract())
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)
    monkeypatch.setattr(core_settings.settings, "quota_enabled", True)
    monkeypatch.setattr(core_settings.settings, "quota_qps_per_user", 0.0)
    monkeypatch.setattr(core_settings.settings, "quota_token_per_user_per_day", 50_000)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_count_toward_quota", True)

    def _block_extract(*_a, **_kw):
        return (False, 49_000, 50_000)

    monkeypatch.setattr(ltm_ex, "check_token_budget_before_main_llm", _block_extract)

    uid = f"u_q_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r = c.post("/chat", json={"message": "配额测", "user_id": uid, "session_id": "sq"})
    assert r.status_code == 200
    assert r.json().get("ltm_extract_written", 0) == 0

    step = next(s for s in c.get(f"/trace/{r.json()['trace_id']}").json()["steps"] if s["name"] == "ltm_extract")
    assert "skipped_quota" in (step.get("output_summary") or "")


def test_ltm_extract_every_n_turns(monkeypatch, trace_mem):
    fake = _FakeLLMExtract()
    _patch_llm_client(monkeypatch, fake)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 2)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_dedup_enabled", False)

    uid = f"u_n_{uuid.uuid4().hex[:8]}"
    c = TestClient(app)
    r1 = c.post("/chat", json={"message": "第一轮", "user_id": uid, "session_id": "s1"})
    assert r1.status_code == 200
    assert r1.json().get("ltm_extract_written", 0) == 0
    n_before = sum(1 for x in fake.calls if "长期记忆抽取助手" in x)

    r2 = c.post("/chat", json={"message": "第二轮", "user_id": uid, "session_id": "s1"})
    assert r2.status_code == 200
    assert r2.json().get("ltm_extract_written", 0) == 1
    n_after = sum(1 for x in fake.calls if "长期记忆抽取助手" in x)
    assert n_after == n_before + 1
