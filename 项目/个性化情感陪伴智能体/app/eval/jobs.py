from __future__ import annotations

import json
import logging
import threading
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from fastapi import HTTPException

logger = logging.getLogger(__name__)

_ROOT = Path(__file__).resolve().parents[2]
_BUILTIN = _ROOT / "data" / "eval_builtin.jsonl"

_lock = threading.Lock()
_jobs: dict[str, EvalJob] = {}


@dataclass
class EvalJob:
    job_id: str
    status: Literal["queued", "running", "done", "failed"] = "queued"
    progress: int = 0
    total: int = 0
    results: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    summary: dict[str, Any] | None = None


def parse_jsonl_lines(text: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        rows.append(json.loads(line))
    return rows


def load_builtin_samples(limit: int) -> list[dict[str, Any]]:
    if not _BUILTIN.is_file():
        return []
    text = _BUILTIN.read_text(encoding="utf-8")
    rows = parse_jsonl_lines(text)
    return rows[:limit]


def create_job(samples: list[dict[str, Any]]) -> str:
    job_id = str(uuid.uuid4())
    with _lock:
        _jobs[job_id] = EvalJob(job_id=job_id, total=len(samples), status="queued")
    return job_id


def get_job(job_id: str) -> EvalJob | None:
    with _lock:
        return _jobs.get(job_id)


def _http_detail(e: HTTPException) -> str:
    d = e.detail
    if isinstance(d, str):
        return d
    try:
        return json.dumps(d, ensure_ascii=False)
    except Exception:
        return str(d)


async def run_eval_job(job_id: str, samples: list[dict[str, Any]], eval_user_id: str) -> None:
    """后台逐条调用 /chat 同源逻辑（直接 await chat）。"""
    from app.api.routes import chat
    from app.api.schemas import ChatRequest

    job = get_job(job_id)
    if job is None:
        return

    with _lock:
        j = _jobs.get(job_id)
        if j:
            j.status = "running"
            j.progress = 0

    results: list[dict[str, Any]] = []
    try:
        for i, row in enumerate(samples):
            msg = (row.get("message") or "").strip()
            if not msg:
                results.append({"index": i, "ok": False, "error": "empty message", "message": ""})
            else:
                sid = f"eval_{job_id[:8]}_{i}"
                t0 = time.perf_counter()
                try:
                    resp = await chat(ChatRequest(message=msg, user_id=eval_user_id, session_id=sid))
                    lat = int((time.perf_counter() - t0) * 1000)
                    results.append(
                        {
                            "index": i,
                            "message": msg,
                            "ok": True,
                            "reply_preview": (resp.reply or "")[:800],
                            "trace_id": resp.trace_id,
                            "latency_ms": lat,
                        }
                    )
                except HTTPException as e:
                    lat = int((time.perf_counter() - t0) * 1000)
                    results.append(
                        {
                            "index": i,
                            "message": msg,
                            "ok": False,
                            "error": _http_detail(e),
                            "latency_ms": lat,
                        }
                    )
                except Exception as e:
                    lat = int((time.perf_counter() - t0) * 1000)
                    logger.exception("eval sample failed")
                    results.append(
                        {
                            "index": i,
                            "message": msg,
                            "ok": False,
                            "error": str(e),
                            "latency_ms": lat,
                        }
                    )

            with _lock:
                j = _jobs.get(job_id)
                if j:
                    j.progress = i + 1
                    j.results = list(results)

        ok_n = sum(1 for r in results if r.get("ok"))
        lats = [int(r["latency_ms"]) for r in results if r.get("ok") and isinstance(r.get("latency_ms"), int)]
        avg = int(sum(lats) / len(lats)) if lats else 0
        summary: dict[str, Any] = {
            "success": ok_n,
            "failed": len(results) - ok_n,
            "avg_latency_ms_ok": avg,
        }
        with _lock:
            j = _jobs.get(job_id)
            if j:
                j.status = "done"
                j.summary = summary
                j.results = list(results)
    except Exception as e:
        logger.exception("eval job crashed")
        with _lock:
            j = _jobs.get(job_id)
            if j:
                j.status = "failed"
                j.error = str(e)
