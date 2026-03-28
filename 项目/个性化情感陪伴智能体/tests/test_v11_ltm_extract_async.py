"""V1.1 P2：隐式 LTM 异步抽取（Trace 合并、后台 job）。"""

from __future__ import annotations

import asyncio

import pytest
from unittest.mock import MagicMock, patch

import app.api.routes as routes
from app.core import settings as core_settings
from app.memory.ltm_extract import merge_ltm_extract_into_stored_trace, process_ltm_extract_job
from app.trace.models import TraceDecision, TraceMetrics, TraceRecord, TraceRequest, TraceStep
from app.trace.store import InMemoryTraceStore
from tests.orchestrator_mocks import patch_llm_client


@pytest.fixture()
def trace_mem(monkeypatch: pytest.MonkeyPatch):
    mem = InMemoryTraceStore()
    monkeypatch.setattr(routes, "trace_store", mem)
    return mem


def test_merge_ltm_extract_into_stored_trace(trace_mem):
    tid = "t-async-1"
    trace_mem.put(
        TraceRecord(
            trace_id=tid,
            request=TraceRequest(
                user_id="u1",
                session_id="s1",
                message="hi",
                timestamp_ms=1,
            ),
            steps=[TraceStep(name="llm_call", start_ms=0, end_ms=100)],
            decision=TraceDecision(
                ltm_extract_written=0,
                ltm_extract_updated=0,
                ltm_extract_new_ids=[],
            ),
            metrics=TraceMetrics(latency_ms=100),
        )
    )
    merge_ltm_extract_into_stored_trace(
        trace_id=tid,
        new_steps=[TraceStep(name="ltm_extract", start_ms=0, end_ms=50, output_summary="written=1")],
        written=1,
        updated=0,
        new_ids=["id-a"],
    )
    rec = trace_mem.get(tid)
    assert rec is not None
    assert len(rec.steps) == 2
    assert rec.steps[1].start_ms == 100
    assert rec.decision.ltm_extract_written == 1
    assert rec.decision.ltm_extract_new_ids == ["id-a"]


def test_process_ltm_extract_job_writes_and_merges(monkeypatch, trace_mem):
    from tests.test_v11_ltm_extract_pipeline import _FakeLLMExtract

    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLMExtract())
    tid = "t-job-1"
    trace_mem.put(
        TraceRecord(
            trace_id=tid,
            request=TraceRequest(
                user_id="u_async",
                session_id="s1",
                message="m",
                timestamp_ms=1,
            ),
            steps=[TraceStep(name="x", start_ms=0, end_ms=10)],
            decision=TraceDecision(
                ltm_extract_written=0,
                ltm_extract_updated=0,
                ltm_extract_new_ids=[],
            ),
            metrics=TraceMetrics(latency_ms=10),
        )
    )

    asyncio.run(
        process_ltm_extract_job(
            {
                "trace_id": tid,
                "user_id": "u_async",
                "session_id": "s1",
                "transcript": "用户: 我不吃辣\n助手: 好的",
                "assistant_n": 1,
                "every_n": 1,
            }
        )
    )
    rec = trace_mem.get(tid)
    assert rec is not None
    assert rec.decision.ltm_extract_written == 1
    assert rec.decision.ltm_extract_new_ids


def test_ltm_extract_async_enqueues_redis(monkeypatch, trace_mem):
    """LTM_EXTRACT_ASYNC + REDIS_URL：入队且响应 pending。"""
    from fastapi.testclient import TestClient

    from tests.test_v11_ltm_extract_pipeline import _FakeLLMExtract

    mock_r = MagicMock()
    patch_llm_client(monkeypatch, _FakeLLMExtract())
    monkeypatch.setattr(core_settings.settings, "ltm_extract_enabled", True)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_every_n_turns", 1)
    monkeypatch.setattr(core_settings.settings, "ltm_extract_async", True)
    monkeypatch.setattr(core_settings.settings, "redis_url", "redis://localhost:6379/15")

    with patch("app.memory.ltm_extract_async.redis.from_url", return_value=mock_r):
        from app.main import app

        c = TestClient(app)
        r = c.post("/chat", json={"message": "我不吃辣", "user_id": "u_q", "session_id": "s_q"})
    assert r.status_code == 200
    body = r.json()
    assert body.get("ltm_extract_async_pending") is True
    assert body.get("ltm_extract_written", 0) == 0
    mock_r.lpush.assert_called_once()
