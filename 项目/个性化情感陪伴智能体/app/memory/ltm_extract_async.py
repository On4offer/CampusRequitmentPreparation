"""
V1.1 P2：隐式 LTM 抽取异步化（依赖 Redis）。
任务入 Redis list，由 uvicorn 进程内 worker（lifespan）BRPOP 消费；无 REDIS_URL 时 `ltm_extract` 回退同步。
"""

from __future__ import annotations

import json
import logging
from typing import Any

import redis

from app.core.settings import settings

logger = logging.getLogger(__name__)

REDIS_QUEUE_KEY = "companion:ltm_extract:queue"


def enqueue_ltm_extract_job(payload: dict[str, Any]) -> None:
    url = (settings.redis_url or "").strip()
    if not url:
        raise RuntimeError("REDIS_URL empty")
    r = redis.from_url(url)
    r.lpush(REDIS_QUEUE_KEY, json.dumps(payload, ensure_ascii=False))


async def ltm_extract_worker_loop() -> None:
    url = (settings.redis_url or "").strip()
    if not url:
        return
    r = redis.from_url(url)
    logger.info("ltm_extract worker started (Redis queue=%s)", REDIS_QUEUE_KEY)
    while True:
        try:
            row = await asyncio.to_thread(r.brpop, REDIS_QUEUE_KEY, 5)
        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("ltm_extract worker BRPOP error")
            await asyncio.sleep(1)
            continue
        if not row:
            continue
        _, raw = row
        try:
            payload = json.loads(raw)
        except json.JSONDecodeError:
            logger.warning("ltm_extract worker bad json: %s", raw[:200])
            continue
        try:
            from app.memory.ltm_extract import process_ltm_extract_job

            await process_ltm_extract_job(payload)
        except Exception:
            logger.exception("ltm_extract worker job failed trace_id=%s", payload.get("trace_id"))
