"""
V1.1：从对话摘录中抽取结构化 LTM（独立 LLM 调用），校验后写入 store 并更新 RAG 索引。

失败只记录日志与 Trace，不向 /chat 抛错。
P2：`LTM_EXTRACT_ASYNC` 时先入队/后台任务，缩短对话尾延迟；完成后回写 Trace。
"""

from __future__ import annotations

import json
import logging
import re
import time
from typing import Any, cast

from app.core.settings import settings
from app.llm.client import ChatMessage, LLMClient, LLMClientError
from app.memory.ltm import LTMItem, LTMType, ltm_store
from app.memory.ltm_dedup import best_match_same_type
from app.memory.store import session_store
from app.quota.limiter import check_token_budget_before_main_llm, consume_main_llm_usage
from app.rag import ltm_retriever
from app.trace.models import TraceStep
from app.trace.store import now_ms

logger = logging.getLogger(__name__)

_VALID_TYPES: frozenset[str] = frozenset({"Preference", "Profile", "Event", "Constraint"})

_EXTRACT_SYSTEM = """你是长期记忆抽取助手。根据下方对话摘录，抽取值得长期保存的用户相关信息。
只输出一个 JSON 对象，不要使用 Markdown 代码块，不要其它解释。格式严格为：
{"items":[{"type":"Preference"|"Profile"|"Event"|"Constraint","content":"简短陈述句","confidence":0.0-1.0,"tags":[]}]}
规则：
- 仅抽取用户明确表达或可合理推断的稳定事实（偏好、自身情况、重要事件、表达的界限或禁忌）。
- 不要编造；没有可存内容时 items 必须为空数组。
- type 含义：Preference 喜好；Profile 自身情况；Event 发生过的事；Constraint 界限或禁忌。
- content 用中文，一条一事，避免过长。
- tags 为简短关键词数组，可空。
- confidence 表示你对该条提取准确性的把握（0~1）。"""


def _strip_json_fence(raw: str) -> str:
    text = raw.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```\s*$", "", text)
    return text.strip()


def _build_transcript(messages: list[ChatMessage], max_chars: int) -> str:
    """从最近一轮往前取，控制在 max_chars 内（时间顺序输出）。"""
    parts_rev: list[str] = []
    used = 0
    for m in reversed(messages):
        role = "用户" if m.role == "user" else "助手" if m.role == "assistant" else m.role
        piece = f"{role}: {m.content or ''}"
        line = piece + "\n"
        if used + len(line) > max_chars:
            break
        parts_rev.append(piece)
        used += len(line)
    return "\n".join(reversed(parts_rev))


def _parse_items(raw_text: str) -> list[dict[str, Any]]:
    data = json.loads(_strip_json_fence(raw_text))
    if not isinstance(data, dict):
        raise ValueError("root must be object")
    items = data.get("items")
    if items is None:
        return []
    if not isinstance(items, list):
        raise ValueError("items must be array")
    out: list[dict[str, Any]] = []
    for it in items:
        if isinstance(it, dict):
            out.append(it)
    return out


def _coerce_item(raw: dict[str, Any], *, min_confidence: float) -> LTMItem | None:
    t = raw.get("type")
    if t not in _VALID_TYPES:
        return None
    content = (raw.get("content") or "").strip()
    if not content or len(content) > 4000:
        return None
    try:
        conf = float(raw.get("confidence", 0.0))
    except (TypeError, ValueError):
        return None
    if conf < min_confidence:
        return None
    tags_raw = raw.get("tags")
    tags: list[str] = []
    if isinstance(tags_raw, list):
        for x in tags_raw[:20]:
            if isinstance(x, str) and (s := x.strip()):
                tags.append(s[:64])
    ts = now_ms()
    return LTMItem(
        id="",
        user_id="",
        type=cast(LTMType, t),
        content=content,
        created_at=ts,
        source="dialogue_extract",
        confidence=min(1.0, max(0.0, conf)),
        tags=tags,
        is_active=True,
        updated_at=ts,
        embedding_status="ready",
    )


def merge_ltm_extract_into_stored_trace(
    *,
    trace_id: str,
    new_steps: list[TraceStep],
    written: int,
    updated: int,
    new_ids: list[str],
) -> None:
    """异步抽取完成后：把步骤与 decision 中的 LTM 字段合并进已落盘的 Trace。"""
    from app.api.routes import trace_store

    rec = trace_store.get(trace_id)
    if rec is None:
        logger.warning("ltm_extract async: trace_id=%s not found, skip merge", trace_id)
        return
    anchor = max((s.end_ms for s in rec.steps), default=0)
    shifted: list[TraceStep] = []
    for st in new_steps:
        shifted.append(
            st.model_copy(
                update={
                    "start_ms": anchor + st.start_ms,
                    "end_ms": anchor + st.end_ms,
                }
            )
        )
    dec = rec.decision.model_copy(
        update={
            "ltm_extract_written": written,
            "ltm_extract_updated": updated,
            "ltm_extract_new_ids": list(new_ids),
        }
    )
    trace_store.put(
        rec.model_copy(
            update={
                "steps": [*rec.steps, *shifted],
                "decision": dec,
            }
        )
    )


async def execute_ltm_extract_pipeline(
    *,
    user_id: str,
    session_id: str,
    transcript: str,
    assistant_n: int,
    every_n: int,
    llm: LLMClient,
    clock_t0: float,
    steps_sink: list[TraceStep],
) -> tuple[int, int, list[str]]:
    """
    执行抽取 LLM + 解析 + 落库 + 索引。所有 ltm_extract 相关 TraceStep 写入 steps_sink；
    时间戳为相对 clock_t0 的毫秒（与同步路径传入 chat 起点 t0 一致；异步 worker 传入本段 pipeline 起点）。
    """

    def _mark_step(
        name: str,
        start_ms: int,
        end_ms: int,
        *,
        input_summary: str | None = None,
        output_summary: str | None = None,
        error: str | None = None,
    ) -> None:
        steps_sink.append(
            TraceStep(
                name=name,
                start_ms=start_ms,
                end_ms=end_ms,
                input_summary=input_summary,
                output_summary=output_summary,
                error=error,
            )
        )

    s_call = time.perf_counter()
    user_payload = f"对话摘录：\n{transcript}"
    prompt_chars = len(_EXTRACT_SYSTEM) + len(user_payload)
    quota_on = bool(getattr(settings, "quota_enabled", False))
    count_ext = bool(getattr(settings, "ltm_extract_count_toward_quota", True))
    day_lim = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
    reply_est = int(getattr(settings, "ltm_extract_quota_reply_estimate", 400) or 400)

    if quota_on and count_ext and day_lim > 0:
        allowed, used_u, _ = check_token_budget_before_main_llm(
            user_id,
            main_prompt_chars=prompt_chars,
            reply_estimate=reply_est,
            limit_per_day=day_lim,
        )
        if not allowed:
            e_call = time.perf_counter()
            _mark_step(
                "ltm_extract",
                start_ms=int((s_call - clock_t0) * 1000),
                end_ms=int((e_call - clock_t0) * 1000),
                input_summary=f"assistant_turns={assistant_n} every_n={every_n}",
                output_summary=f"skipped_quota used={used_u} limit={day_lim}",
            )
            return 0, 0, []

    try:
        resp = await llm.chat(
            [
                ChatMessage(role="system", content=_EXTRACT_SYSTEM),
                ChatMessage(role="user", content=user_payload),
            ],
            temperature=float(getattr(settings, "ltm_extract_llm_temperature", 0.2) or 0.2),
        )
        raw = llm.extract_text(resp).strip()
    except LLMClientError as e:
        e_call = time.perf_counter()
        _mark_step(
            "ltm_extract",
            start_ms=int((s_call - clock_t0) * 1000),
            end_ms=int((e_call - clock_t0) * 1000),
            input_summary=f"assistant_turns={assistant_n} every_n={every_n}",
            error=str(e)[:500],
        )
        logger.warning("ltm_extract llm failed user_id=%s session_id=%s err=%s", user_id, session_id, e)
        return 0, 0, []
    except Exception as e:  # noqa: BLE001
        e_call = time.perf_counter()
        _mark_step(
            "ltm_extract",
            start_ms=int((s_call - clock_t0) * 1000),
            end_ms=int((e_call - clock_t0) * 1000),
            error=f"unexpected:{type(e).__name__}:{e}"[:500],
        )
        logger.exception("ltm_extract unexpected user_id=%s session_id=%s", user_id, session_id)
        return 0, 0, []

    e_call = time.perf_counter()

    if quota_on and count_ext and day_lim > 0:
        consume_main_llm_usage(user_id, prompt_chars, len(raw))

    try:
        raw_items = _parse_items(raw)
    except ValueError as e:
        _mark_step(
            "ltm_extract",
            start_ms=int((s_call - clock_t0) * 1000),
            end_ms=int((e_call - clock_t0) * 1000),
            input_summary=f"assistant_turns={assistant_n} every_n={every_n}",
            error=f"parse_failed:{e}"[:500],
        )
        logger.warning("ltm_extract parse failed user_id=%s err=%s raw_prefix=%s", user_id, e, raw[:200])
        return 0, 0, []

    min_c = float(getattr(settings, "ltm_extract_min_confidence", 0.55) or 0.0)
    cap = max(1, int(getattr(settings, "ltm_extract_max_items", 5) or 5))

    dedup_on = bool(getattr(settings, "ltm_extract_dedup_enabled", True))
    skip_r = float(getattr(settings, "ltm_extract_dedup_skip_ratio", 0.9) or 0.9)
    merge_r = float(getattr(settings, "ltm_extract_dedup_merge_ratio", 0.76) or 0.76)
    if merge_r >= skip_r:
        merge_r = max(0.0, skip_r - 0.01)
    lookback = max(10, int(getattr(settings, "ltm_extract_dedup_lookback", 80) or 80))

    pool: list[LTMItem] = []
    if dedup_on:
        try:
            rows, _ = ltm_store.list_by_user(user_id, limit=lookback, offset=0, only_active=True)
            pool = list(rows)
        except Exception as e:  # noqa: BLE001
            logger.warning("ltm_extract dedup load failed user_id=%s err=%s", user_id, e)

    written = 0
    updated = 0
    skipped_dup = 0
    new_ids: list[str] = []
    for raw_it in raw_items[:cap]:
        if not isinstance(raw_it, dict):
            continue
        item = _coerce_item(raw_it, min_confidence=min_c)
        if item is None:
            continue
        try:
            if dedup_on and pool:
                match, sim = best_match_same_type(content=item.content, typ=item.type, candidates=pool)
                if match is not None and sim >= skip_r:
                    skipped_dup += 1
                    continue
                if match is not None and sim >= merge_r:
                    ts_u = now_ms()
                    merged_tags = list(dict.fromkeys([*(match.tags or []), *(item.tags or [])]))[:30]
                    nconf = max(match.confidence, item.confidence)
                    if item.confidence > match.confidence:
                        ncontent = item.content
                    elif item.confidence < match.confidence:
                        ncontent = match.content
                    else:
                        ncontent = item.content if len(item.content) >= len(match.content) else match.content
                    upd = ltm_store.update_item(
                        id=match.id,
                        content=ncontent,
                        tags=merged_tags,
                        confidence=nconf,
                        updated_at=ts_u,
                    )
                    if upd:
                        ltm_retriever.index_item(upd)
                        replaced = False
                        for i, p in enumerate(pool):
                            if p.id == upd.id:
                                pool[i] = upd
                                replaced = True
                                break
                        if not replaced:
                            pool.append(upd)
                        updated += 1
                    continue

            lid = ltm_store.put(user_id, item)
            item_ok = item.model_copy(update={"id": lid, "user_id": user_id})
            ltm_retriever.index_item(item_ok)
            pool.append(item_ok)
            new_ids.append(lid)
            written += 1
        except Exception as e:  # noqa: BLE001
            logger.warning("ltm_extract put/index failed user_id=%s err=%s", user_id, e)

    e2 = time.perf_counter()
    _mark_step(
        "ltm_extract",
        start_ms=int((s_call - clock_t0) * 1000),
        end_ms=int((e2 - clock_t0) * 1000),
        input_summary=f"assistant_turns={assistant_n} every_n={every_n} raw_items={len(raw_items)}",
        output_summary=f"written={written} updated={updated} skipped_dup={skipped_dup}",
    )
    return written, updated, new_ids


async def process_ltm_extract_job(payload: dict[str, Any]) -> None:
    """后台/队列消费：执行抽取并合并 Trace。"""
    try:
        from app.llm.factory import build_llm_client

        llm = build_llm_client()
    except Exception as e:
        logger.error("ltm_extract async job: cannot build LLM client: %s", e)
        return

    trace_id = str(payload.get("trace_id") or "")
    user_id = str(payload.get("user_id") or "")
    session_id = str(payload.get("session_id") or "")
    transcript = str(payload.get("transcript") or "")
    assistant_n = int(payload.get("assistant_n") or 0)
    every_n = int(payload.get("every_n") or 0)
    if not trace_id or not user_id or not transcript.strip():
        return

    steps_acc: list[TraceStep] = []
    t0 = time.perf_counter()
    w, u, ids = await execute_ltm_extract_pipeline(
        user_id=user_id,
        session_id=session_id,
        transcript=transcript,
        assistant_n=assistant_n,
        every_n=every_n,
        llm=llm,
        clock_t0=t0,
        steps_sink=steps_acc,
    )
    merge_ltm_extract_into_stored_trace(
        trace_id=trace_id,
        new_steps=steps_acc,
        written=w,
        updated=u,
        new_ids=ids,
    )


async def maybe_extract_ltm_after_chat(
    *,
    trace_id: str,
    user_id: str,
    session_id: str,
    llm: LLMClient,
    safety_mode: bool,
    steps: list[TraceStep],
    t0: float,
) -> tuple[int, int, list[str], bool]:
    """
    在 STM 已写入本轮 user+assistant 之后调用。
    返回 (新建条数, 合并更新条数, 新建 id 列表, 是否已异步排队/后台执行)。
    """

    def _mark_step(
        name: str,
        start_ms: int,
        end_ms: int,
        *,
        input_summary: str | None = None,
        output_summary: str | None = None,
        error: str | None = None,
    ) -> None:
        steps.append(
            TraceStep(
                name=name,
                start_ms=start_ms,
                end_ms=end_ms,
                input_summary=input_summary,
                output_summary=output_summary,
                error=error,
            )
        )

    if not getattr(settings, "ltm_extract_enabled", False):
        return 0, 0, [], False
    if safety_mode:
        s0 = time.perf_counter()
        _mark_step(
            "ltm_extract",
            start_ms=int((s0 - t0) * 1000),
            end_ms=int((s0 - t0) * 1000),
            output_summary="skipped safety_mode",
        )
        return 0, 0, [], False

    every_n = int(getattr(settings, "ltm_extract_every_n_turns", 0) or 0)
    if every_n <= 0:
        return 0, 0, [], False

    msgs = session_store.get_messages(user_id=user_id, session_id=session_id)
    if not msgs:
        return 0, 0, [], False

    assistant_n = sum(1 for m in msgs if m.role == "assistant")
    if assistant_n % every_n != 0:
        return 0, 0, [], False

    budget = max(500, int(getattr(settings, "ltm_extract_char_budget", 6000) or 6000))
    transcript = _build_transcript(msgs, budget)
    if not transcript.strip():
        return 0, 0, [], False

    if getattr(settings, "ltm_extract_async", False):
        redis_url = (getattr(settings, "redis_url", "") or "").strip()
        if redis_url:
            payload = {
                "trace_id": trace_id,
                "user_id": user_id,
                "session_id": session_id,
                "transcript": transcript,
                "assistant_n": assistant_n,
                "every_n": every_n,
            }
            from app.memory.ltm_extract_async import enqueue_ltm_extract_job

            s_q = time.perf_counter()
            try:
                enqueue_ltm_extract_job(payload)
                _mark_step(
                    "ltm_extract",
                    start_ms=int((s_q - t0) * 1000),
                    end_ms=int((s_q - t0) * 1000),
                    input_summary=f"assistant_turns={assistant_n} every_n={every_n}",
                    output_summary="queued_redis",
                )
                return 0, 0, [], True
            except Exception as e:  # noqa: BLE001
                logger.warning("ltm_extract redis enqueue failed, fallback sync: %s", e)
        else:
            logger.warning(
                "ltm_extract_async=True but REDIS_URL empty: async queue unavailable, running sync extract"
            )

    w, u, ids = await execute_ltm_extract_pipeline(
        user_id=user_id,
        session_id=session_id,
        transcript=transcript,
        assistant_n=assistant_n,
        every_n=every_n,
        llm=llm,
        clock_t0=t0,
        steps_sink=steps,
    )
    return w, u, ids, False
