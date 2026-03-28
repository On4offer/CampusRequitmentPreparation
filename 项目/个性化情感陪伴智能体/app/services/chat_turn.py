"""
/chat 主链路：准备 LLM 消息（情绪/RAG/工具/STM/配额）与收尾（脱敏、写 STM、写 Trace）。

从 routes 抽出以便 /chat 与 /chat/stream 复用；trace_store 运行时从 app.api.routes 读取以兼容测试 monkeypatch。
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from collections.abc import AsyncIterator
from typing import Any

from fastapi import HTTPException

from app.api.chat_constants import (
    DEFAULT_QUOTA_DEGRADE_HINT,
    LTM_RAG_EVIDENCE_HEADER,
    SAFE_SYSTEM_PROMPT,
    TOOL_RESULT_SYSTEM_SUFFIX_HEADER,
)
from app.api.schemas import ChatRequest, ChatResponse
from app.core.settings import settings
from app.emotion import analyze_emotion
from app.emotion.log import append_emotion_record
from app.llm.client import ChatMessage, LLMClient
from app.llm.user_visible_errors import llm_error_detail_for_client
from app.memory.ltm_extract import maybe_extract_ltm_after_chat
from app.memory.store import session_store
from app.policy import decide_mode, get_system_prompt_for_mode
from app.quota.limiter import (
    check_qps,
    check_token_budget_before_main_llm,
    consume_emotion_estimate,
    consume_main_llm_usage,
    get_daily_usage,
)
from app.safety.content_filter import merge_safety_trace_reason, sanitize_assistant_output, scan_user_input
from app.tools.router import route_tool_params
from app.trace.models import TraceDecision, TraceMetrics, TraceRecord, TraceRequest, TraceStep
from app.trace.store import now_ms

logger = logging.getLogger(__name__)


def _routes_trace_store():
    import app.api.routes as routes_mod

    return routes_mod.trace_store


def _routes_build_llm():
    """与测试 monkeypatch `routes._build_llm_client` 对齐。"""
    import app.api.routes as routes_mod

    return routes_mod._build_llm_client()


def _trace_safety_kwargs(
    safety_mode: bool,
    safety_trigger_reason: str | None,
    output_filter_tags: list[str] | None,
) -> dict:
    st, sr = merge_safety_trace_reason(
        safety_mode=safety_mode,
        safety_trigger_reason=safety_trigger_reason,
        output_filter_tags=output_filter_tags or [],
    )
    return {"safety_triggered": st, "safety_reason": sr}


@dataclass
class ChatTurnPrepared:
    t0: float
    trace_id: str
    user_id: str
    session_id: str
    request_ts: int
    req: ChatRequest
    steps: list[TraceStep]
    llm: LLMClient
    messages: list[ChatMessage]
    history_message_count: int
    emotion_for_trace: dict[str, Any]
    mode: str
    mode_reason: str
    safety_mode: bool
    safety_trigger_reason: str | None
    intended_tool: str | None
    tool_params_placeholder: str | None
    tool_selected: str | None
    tool_status: str | None
    tool_error: str | None
    tool_summary: dict | None
    memory_hits: list | None
    citations: list | None
    quota_degraded_mode: bool
    lc_chat_model: Any | None = None


async def prepare_chat_until_llm(req: ChatRequest) -> ChatTurnPrepared:
    trace_store = _routes_trace_store()
    t0 = time.perf_counter()
    trace_id = str(uuid.uuid4())
    user_id = session_store.ensure_user_id(req.user_id)
    session_id = session_store.ensure_session_id(req.session_id)
    steps: list[TraceStep] = []
    request_ts = now_ms()
    quota_degraded_mode = False

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

    input_scan = None
    if getattr(settings, "content_safety_enabled", True):
        input_scan = scan_user_input(req.message)
        if input_scan.force_safety or input_scan.matched_categories:
            s_cs = time.perf_counter()
            _mark_step(
                "content_safety_input",
                start_ms=0,
                end_ms=int((s_cs - t0) * 1000),
                input_summary=f"categories={','.join(input_scan.matched_categories)} force_safety={input_scan.force_safety}",
            )

    if getattr(settings, "quota_enabled", False):
        qps = float(getattr(settings, "quota_qps_per_user", 0) or 0)
        if qps > 0 and not check_qps(user_id, max_per_second=qps):
            used = get_daily_usage(user_id)
            lim = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
            latency_ms = int((time.perf_counter() - t0) * 1000)
            trace_store.put(
                TraceRecord(
                    trace_id=trace_id,
                    request=TraceRequest(
                        user_id=user_id,
                        session_id=session_id,
                        message=req.message,
                        timestamp_ms=request_ts,
                    ),
                    steps=[
                        TraceStep(
                            name="quota_qps",
                            start_ms=0,
                            end_ms=latency_ms,
                            error="qps_exceeded",
                        )
                    ],
                    decision=TraceDecision(
                        quota_used_today=used,
                        quota_limit=lim if lim > 0 else None,
                        quota_exceeded=True,
                        degraded_mode=False,
                        safety_triggered=False,
                        safety_reason=None,
                    ),
                    metrics=TraceMetrics(latency_ms=latency_ms, model=settings.llm_model, degraded=True),
                )
            )
            raise HTTPException(
                status_code=429,
                detail={"error": "rate_limited", "message": "请求过于频繁，请稍后再试。"},
            )

    llm = _routes_build_llm()
    emotion_result = await analyze_emotion(req.message, llm=llm)
    content_force_safety = bool(input_scan and input_scan.force_safety)
    emotion_high = emotion_result.risk_tier == "高风险"
    safety_mode = emotion_high or content_force_safety
    _reason_parts: list[str] = []
    if emotion_high:
        _reason_parts.append(emotion_result.evidence or "高风险关键词")
    if content_force_safety and input_scan:
        _reason_parts.append("内容安全输入:" + ",".join(input_scan.matched_categories))
    safety_trigger_reason = "; ".join(_reason_parts) if safety_mode else None
    mode, mode_reason, intended_tool, tool_params_placeholder = decide_mode(
        req.message, str(emotion_result.label), emotion_result.intensity
    )
    if safety_mode and getattr(settings, "safety_force_listen", True):
        mode, mode_reason = "倾听", "高风险安全模式优先倾听"
        intended_tool, tool_params_placeholder = None, None
    elif emotion_result.risk_tier == "关注" and getattr(settings, "watch_tier_force_listen", True):
        mode, mode_reason = "倾听", "关注档优先倾听"
        intended_tool, tool_params_placeholder = None, None
    system = SAFE_SYSTEM_PROMPT if safety_mode else get_system_prompt_for_mode(mode)
    emotion_for_trace = {
        "label": emotion_result.label,
        "intensity": emotion_result.intensity,
        "evidence": emotion_result.evidence,
        "risk_tier": emotion_result.risk_tier,
    }

    if getattr(settings, "quota_enabled", False) and int(getattr(settings, "quota_token_per_user_per_day", 0) or 0) > 0:
        consume_emotion_estimate(user_id)

    memory_hits: list | None = None
    citations: list | None = None
    system_core = system
    tool_result_text: str | None = None
    tool_selected: str | None = None
    tool_status: str | None = None
    tool_error: str | None = None
    tool_elapsed_ms: float = 0.0

    if getattr(settings, "emotion_log_enabled", False) and settings.emotion_log_path:
        append_emotion_record(
            settings.emotion_log_path,
            {
                "user_id": user_id,
                "session_id": session_id,
                "timestamp_ms": request_ts,
                "label": emotion_for_trace["label"],
                "intensity": emotion_for_trace["intensity"],
                "risk_tier": emotion_for_trace["risk_tier"],
                "trace_id": trace_id,
            },
        )

    if getattr(settings, "rag_enabled", False):
        s_rag = time.perf_counter()
        try:
            top_k = getattr(settings, "rag_top_k", 3)
            use_hybrid = getattr(settings, "rag_use_hybrid", False)
            from app.langchain.rag_lcel import build_ltm_rag_via_lcel

            memory_hits, citations, evidence_body, rewrite_triggered, rewritten_query = await build_ltm_rag_via_lcel(
                user_id=user_id,
                user_message=req.message,
                llm=llm,
            )
            if evidence_body:
                system = system + LTM_RAG_EVIDENCE_HEADER + evidence_body
            nh = len(memory_hits) if memory_hits else 0
            ids = [x.get("id") for x in (memory_hits or []) if x.get("id") is not None]
            out_summary = f"hits={nh} ids={ids} lcel=true"
            if rewrite_triggered and rewritten_query:
                out_summary += f" rewrite_triggered=true rewritten_query={rewritten_query[:50]}"

            e_rag = time.perf_counter()
            _mark_step(
                "retrieve_ltm",
                start_ms=int((s_rag - t0) * 1000),
                end_ms=int((e_rag - t0) * 1000),
                input_summary=f"query_len={len(req.message)} top_k={top_k} hybrid={use_hybrid}",
                output_summary=out_summary,
            )
        except Exception as e:
            _mark_step(
                "retrieve_ltm",
                start_ms=int((s_rag - t0) * 1000),
                end_ms=int((time.perf_counter() - t0) * 1000),
                input_summary=f"query_len={len(req.message)}",
                error=str(e),
            )

    if getattr(settings, "tool_enabled", False) and intended_tool in ("time", "weather"):
        s_tool = time.perf_counter()
        params = route_tool_params(intended_tool, req.message)
        _mark_step(
            "tool_route",
            start_ms=int((s_tool - t0) * 1000),
            end_ms=int((time.perf_counter() - t0) * 1000),
            input_summary=f"tool={intended_tool} params={params}",
            output_summary=f"routed to {intended_tool}",
        )
        timeout_s = getattr(settings, "tool_timeout_s", 5.0)
        retry_times = getattr(settings, "tool_retry_times", 1)
        from app.langchain.tools_lc import run_policy_tool_via_structured_tool

        result, elapsed_ms = run_policy_tool_via_structured_tool(
            intended_tool,
            params,
            timeout_s=timeout_s,
            retry_times=retry_times,
        )
        e_tool = time.perf_counter()
        tool_exec_summary = f"success={result.success} elapsed_ms={elapsed_ms:.0f} structured_tool=1"
        _mark_step(
            "tool_execute",
            start_ms=int((s_tool - t0) * 1000),
            end_ms=int((e_tool - t0) * 1000),
            input_summary=f"tool={intended_tool} params={params}",
            output_summary=tool_exec_summary if result.success else None,
            error=result.error.message if result.error else None,
        )
        tool_selected = intended_tool
        tool_status = "success" if result.success else "failed"
        tool_error = result.error.message if result.error else None
        tool_elapsed_ms = elapsed_ms
        if result.success and result.raw_text:
            tool_result_text = result.raw_text

    tool_summary = None
    if tool_selected:
        tool_summary = {
            "tool": tool_selected,
            "status": tool_status,
            "elapsed_ms": round(tool_elapsed_ms),
        }
        if tool_error:
            tool_summary["error"] = tool_error

    if tool_result_text:
        system = system + TOOL_RESULT_SYSTEM_SUFFIX_HEADER + tool_result_text

    s1 = time.perf_counter()
    state = session_store.get_or_create(user_id=user_id, session_id=session_id)
    from app.langchain.stm_history import SessionStoreChatMessageHistory

    _stm_hist = SessionStoreChatMessageHistory(
        user_id=user_id,
        session_id=session_id,
        max_chars=settings.stm_max_chars,
    )
    history = _stm_hist.get_trimmed_chat_messages()
    messages = [ChatMessage(role="system", content=system), *history, ChatMessage(role="user", content=req.message)]
    e1 = time.perf_counter()
    stm_out = f"history_after={len(history)} messages_for_llm={len(messages)} base_chat_message_history=1"
    _mark_step(
        "load_session_and_trim_stm",
        start_ms=int((s1 - t0) * 1000),
        end_ms=int((e1 - t0) * 1000),
        input_summary=f"history_before={len(state.messages)} max_chars={settings.stm_max_chars}",
        output_summary=stm_out,
    )

    if getattr(settings, "quota_enabled", False):
        lim_day = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
        if lim_day > 0:
            main_chars = sum(len(m.content or "") for m in messages)
            allowed_q, used_q, lim_q = check_token_budget_before_main_llm(
                user_id,
                main_prompt_chars=main_chars,
                limit_per_day=lim_day,
            )
            if not allowed_q:
                degrade_ok = False
                if bool(getattr(settings, "quota_degrade_on_exhaust", False)):
                    custom_hint = (getattr(settings, "quota_degrade_system_hint", "") or "").strip()
                    hint_text = custom_hint if custom_hint else DEFAULT_QUOTA_DEGRADE_HINT
                    variants: list[tuple[str, str]] = [
                        ("strip_rag_with_hint", system_core + "\n\n" + hint_text),
                        ("strip_rag_only", system_core),
                    ]
                    for vname, sys_body in variants:
                        trial_messages = [
                            ChatMessage(role="system", content=sys_body),
                            *history,
                            ChatMessage(role="user", content=req.message),
                        ]
                        trial_chars = sum(len(m.content or "") for m in trial_messages)
                        ok_trial, used_trial, lim_trial = check_token_budget_before_main_llm(
                            user_id,
                            main_prompt_chars=trial_chars,
                            limit_per_day=lim_day,
                        )
                        if ok_trial:
                            qd = time.perf_counter()
                            _mark_step(
                                "quota_degraded",
                                start_ms=int((s1 - t0) * 1000),
                                end_ms=int((qd - t0) * 1000),
                                input_summary=(
                                    f"used={used_q} limit={lim_q} main_chars_before={main_chars} variant={vname} "
                                    f"trial_main_chars={trial_chars}"
                                ),
                                output_summary="rebuilt_prompt_without_rag",
                            )
                            system = sys_body
                            messages = trial_messages
                            memory_hits = None
                            citations = None
                            used_q, lim_q = used_trial, lim_trial
                            quota_degraded_mode = True
                            degrade_ok = True
                            break
                if not degrade_ok:
                    e2 = time.perf_counter()
                    _mark_step(
                        "quota_check",
                        start_ms=int((s1 - t0) * 1000),
                        end_ms=int((e2 - t0) * 1000),
                        input_summary=f"used={used_q} limit={lim_q} main_chars={main_chars}",
                        error="daily_quota_exceeded",
                    )
                    latency_ms = int((time.perf_counter() - t0) * 1000)
                    trace_store.put(
                        TraceRecord(
                            trace_id=trace_id,
                            request=TraceRequest(
                                user_id=user_id,
                                session_id=session_id,
                                message=req.message,
                                timestamp_ms=request_ts,
                            ),
                            steps=steps,
                            decision=TraceDecision(
                                emotion=emotion_for_trace,
                                mode=mode,
                                mode_reason=mode_reason,
                                safety_mode=safety_mode,
                                safety_trigger_reason=safety_trigger_reason,
                                intended_tool=intended_tool,
                                tool_params_placeholder=tool_params_placeholder,
                                tool_selected=tool_selected,
                                tool_status=tool_status,
                                tool_error=tool_error,
                                memory_hits=memory_hits,
                                quota_used_today=used_q,
                                quota_limit=lim_q,
                                quota_exceeded=True,
                                degraded_mode=False,
                                **_trace_safety_kwargs(safety_mode, safety_trigger_reason, []),
                            ),
                            metrics=TraceMetrics(latency_ms=latency_ms, model=settings.llm_model, degraded=True),
                        )
                    )
                    raise HTTPException(
                        status_code=429,
                        detail={
                            "error": "quota_exceeded",
                            "message": "今日对话额度已用尽，请明日再试或联系管理员。",
                            "quota_used": used_q,
                            "quota_limit": lim_q,
                        },
                    )

    from app.langchain.chat_model import build_chat_openai_from_settings

    lc_chat_model = build_chat_openai_from_settings()

    return ChatTurnPrepared(
        t0=t0,
        trace_id=trace_id,
        user_id=user_id,
        session_id=session_id,
        request_ts=request_ts,
        req=req,
        steps=steps,
        llm=llm,
        messages=messages,
        history_message_count=len(history),
        emotion_for_trace=emotion_for_trace,
        mode=mode,
        mode_reason=mode_reason,
        safety_mode=safety_mode,
        safety_trigger_reason=safety_trigger_reason,
        intended_tool=intended_tool,
        tool_params_placeholder=tool_params_placeholder,
        tool_selected=tool_selected,
        tool_status=tool_status,
        tool_error=tool_error,
        tool_summary=tool_summary,
        memory_hits=memory_hits,
        citations=citations,
        quota_degraded_mode=quota_degraded_mode,
        lc_chat_model=lc_chat_model,
    )


async def finalize_chat_turn(
    prepared: ChatTurnPrepared,
    *,
    reply: str,
    llm_request_id: str | None,
    llm_started_s: float,
    llm_ended_s: float,
    streamed: bool = False,
) -> ChatResponse:
    trace_store = _routes_trace_store()
    p = prepared
    t0 = p.t0
    req = p.req
    steps = p.steps

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

    s2_ms = int((llm_started_s - t0) * 1000)
    e2_ms = int((llm_ended_s - t0) * 1000)
    _mark_step(
        "llm_call",
        start_ms=s2_ms,
        end_ms=e2_ms,
        input_summary=f"messages={len(p.messages)} model={settings.llm_model} stream={streamed}",
        output_summary=f"llm_request_id={llm_request_id}",
    )

    output_sanitize_hits: list[str] = []
    reply_stripped = reply.strip()
    if getattr(settings, "content_safety_enabled", True) and getattr(settings, "content_safety_filter_output", True):
        reply_stripped, output_sanitize_hits = sanitize_assistant_output(reply_stripped)
        if output_sanitize_hits:
            s_out = time.perf_counter()
            _mark_step(
                "content_safety_output",
                start_ms=s2_ms,
                end_ms=int((s_out - t0) * 1000),
                output_summary=f"tags={','.join(output_sanitize_hits)}",
            )

    if not reply_stripped:
        latency_ms = int((time.perf_counter() - t0) * 1000)
        _mark_step("extract_text", start_ms=latency_ms, end_ms=latency_ms, error="empty_reply")
        trace_store.put(
            TraceRecord(
                trace_id=p.trace_id,
                request=TraceRequest(
                    user_id=p.user_id,
                    session_id=p.session_id,
                    message=req.message,
                    timestamp_ms=p.request_ts,
                ),
                steps=steps,
                decision=TraceDecision(
                    emotion=p.emotion_for_trace,
                    mode=p.mode,
                    mode_reason=p.mode_reason,
                    safety_mode=p.safety_mode,
                    safety_trigger_reason=p.safety_trigger_reason,
                    intended_tool=p.intended_tool,
                    tool_params_placeholder=p.tool_params_placeholder,
                    tool_selected=p.tool_selected,
                    tool_status=p.tool_status,
                    tool_error=p.tool_error,
                    memory_hits=p.memory_hits,
                    quota_used_today=get_daily_usage(p.user_id) if getattr(settings, "quota_enabled", False) else None,
                    quota_limit=int(getattr(settings, "quota_token_per_user_per_day", 0) or 0) or None,
                    quota_exceeded=bool(p.quota_degraded_mode),
                    degraded_mode=bool(p.quota_degraded_mode),
                    ltm_extract_written=0,
                    ltm_extract_updated=0,
                    ltm_extract_new_ids=[],
                    **_trace_safety_kwargs(p.safety_mode, p.safety_trigger_reason, output_sanitize_hits),
                ),
                metrics=TraceMetrics(
                    latency_ms=latency_ms,
                    token_in=None,
                    token_out=None,
                    model=settings.llm_model,
                    degraded=True,
                ),
            )
        )
        raise HTTPException(status_code=502, detail="Empty model response.")

    s3 = time.perf_counter()
    session_store.append(user_id=p.user_id, session_id=p.session_id, message=ChatMessage(role="user", content=req.message))
    session_store.append(
        user_id=p.user_id,
        session_id=p.session_id,
        message=ChatMessage(role="assistant", content=reply_stripped),
    )
    e3 = time.perf_counter()
    _mark_step(
        "persist_memory",
        start_ms=int((s3 - t0) * 1000),
        end_ms=int((e3 - t0) * 1000),
        output_summary="appended user+assistant messages to session_store",
    )

    token_in_est = sum(len(m.content or "") for m in p.messages)
    token_out_est = len(reply_stripped)
    if getattr(settings, "quota_enabled", False) and int(getattr(settings, "quota_token_per_user_per_day", 0) or 0) > 0:
        consume_main_llm_usage(p.user_id, token_in_est, token_out_est)

    ltm_written, ltm_updated, ltm_new_ids, ltm_async_pending = await maybe_extract_ltm_after_chat(
        trace_id=p.trace_id,
        user_id=p.user_id,
        session_id=p.session_id,
        llm=p.llm,
        safety_mode=p.safety_mode,
        steps=steps,
        t0=t0,
    )

    latency_ms = int((time.perf_counter() - t0) * 1000)
    q_lim = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
    trace_store.put(
        TraceRecord(
            trace_id=p.trace_id,
            request=TraceRequest(
                user_id=p.user_id,
                session_id=p.session_id,
                message=req.message,
                timestamp_ms=p.request_ts,
            ),
            steps=steps,
            decision=TraceDecision(
                emotion=p.emotion_for_trace,
                mode=p.mode,
                mode_reason=p.mode_reason,
                safety_mode=p.safety_mode,
                safety_trigger_reason=p.safety_trigger_reason,
                intended_tool=p.intended_tool,
                tool_params_placeholder=p.tool_params_placeholder,
                tool_selected=p.tool_selected,
                tool_status=p.tool_status,
                tool_error=p.tool_error,
                memory_hits=p.memory_hits,
                quota_used_today=get_daily_usage(p.user_id) if getattr(settings, "quota_enabled", False) else None,
                quota_limit=q_lim if q_lim > 0 and getattr(settings, "quota_enabled", False) else None,
                quota_exceeded=bool(p.quota_degraded_mode),
                degraded_mode=bool(p.quota_degraded_mode),
                ltm_extract_written=ltm_written,
                ltm_extract_updated=ltm_updated,
                ltm_extract_new_ids=list(ltm_new_ids),
                **_trace_safety_kwargs(p.safety_mode, p.safety_trigger_reason, output_sanitize_hits),
            ),
            metrics=TraceMetrics(
                latency_ms=latency_ms,
                token_in=token_in_est,
                token_out=token_out_est,
                model=settings.llm_model,
                degraded=bool(p.quota_degraded_mode),
            ),
        )
    )

    logger.info(
        "chat_done trace_id=%s latency_ms=%s mode=%s risk_tier=%s user_id=%s stream=%s ltm_written=%s ltm_updated=%s ltm_new_ids=%s",
        p.trace_id,
        latency_ms,
        p.mode,
        p.emotion_for_trace.get("risk_tier"),
        p.user_id,
        streamed,
        ltm_written,
        ltm_updated,
        len(ltm_new_ids),
    )

    debug = None
    if settings.debug:
        debug = {
            "trace_id": p.trace_id,
            "latency_ms": latency_ms,
            "llm_request_id": llm_request_id,
            "model": settings.llm_model,
            "user_id": p.user_id,
            "session_id": p.session_id,
            "history_messages": p.history_message_count,
            "stream": streamed,
        }

    return ChatResponse(
        reply=reply_stripped,
        trace_id=p.trace_id,
        user_id=p.user_id,
        session_id=p.session_id,
        debug=debug,
        citations=p.citations,
        tool_summary=p.tool_summary,
        quota_degraded=bool(p.quota_degraded_mode),
        ltm_extract_written=ltm_written,
        ltm_extract_updated=ltm_updated,
        ltm_extract_new_ids=list(ltm_new_ids),
        ltm_extract_async_pending=ltm_async_pending,
    )


async def iter_chat_llm_text_deltas(
    prepared: ChatTurnPrepared,
    meta_out: dict[str, str | None],
) -> AsyncIterator[str]:
    """流式主 LLM：`ChatPromptTemplate | ChatModel` 链的 `astream`。"""
    from app.langchain.llm_trace_callback import LlmProviderIdCallback
    from app.langchain.main_chain import build_main_chat_lc_chain
    from app.langchain.messages import chat_messages_to_lc

    lc_msgs = chat_messages_to_lc(prepared.messages)
    chain = build_main_chat_lc_chain(prepared.lc_chat_model)
    cb_sink: dict[str, str | None] = {}
    handler = LlmProviderIdCallback(cb_sink)
    cfg = {"callbacks": [handler]}
    async for chunk in chain.astream({"messages": lc_msgs}, config=cfg):
        if isinstance(chunk, str) and chunk:
            yield chunk
    rid = cb_sink.get("request_id")
    if isinstance(rid, str):
        meta_out["request_id"] = rid


async def run_llm_chat_and_finalize(prepared: ChatTurnPrepared) -> ChatResponse:
    """非流式：LCEL 主链 `ainvoke` + finalize。"""
    trace_store = _routes_trace_store()
    s2 = time.perf_counter()
    from app.langchain.llm_trace_callback import LlmProviderIdCallback
    from app.langchain.main_chain import build_main_chat_lc_chain
    from app.langchain.messages import chat_messages_to_lc

    lc_msgs = chat_messages_to_lc(prepared.messages)
    chain = build_main_chat_lc_chain(prepared.lc_chat_model)
    cb_sink: dict[str, str | None] = {}
    handler = LlmProviderIdCallback(cb_sink)
    cfg = {"callbacks": [handler]}
    try:
        reply_text = await chain.ainvoke({"messages": lc_msgs}, config=cfg)
    except Exception as e:
        e2 = time.perf_counter()
        prepared.steps.append(
            TraceStep(
                name="llm_call",
                start_ms=int((s2 - prepared.t0) * 1000),
                end_ms=int((e2 - prepared.t0) * 1000),
                input_summary=(
                    f"messages={len(prepared.messages)} model={settings.llm_model} "
                    "lcel=ChatPromptTemplate|ChatModel|StrOutputParser"
                ),
                error=str(e),
            )
        )
        latency_ms = int((time.perf_counter() - prepared.t0) * 1000)
        trace_store.put(
            TraceRecord(
                trace_id=prepared.trace_id,
                request=TraceRequest(
                    user_id=prepared.user_id,
                    session_id=prepared.session_id,
                    message=prepared.req.message,
                    timestamp_ms=prepared.request_ts,
                ),
                steps=prepared.steps,
                decision=TraceDecision(
                    emotion=prepared.emotion_for_trace,
                    mode=prepared.mode,
                    mode_reason=prepared.mode_reason,
                    safety_mode=prepared.safety_mode,
                    safety_trigger_reason=prepared.safety_trigger_reason,
                    intended_tool=prepared.intended_tool,
                    tool_params_placeholder=prepared.tool_params_placeholder,
                    tool_selected=prepared.tool_selected,
                    tool_status=prepared.tool_status,
                    tool_error=prepared.tool_error,
                    memory_hits=prepared.memory_hits,
                    quota_used_today=get_daily_usage(prepared.user_id) if getattr(settings, "quota_enabled", False) else None,
                    quota_limit=int(getattr(settings, "quota_token_per_user_per_day", 0) or 0) or None,
                    quota_exceeded=bool(prepared.quota_degraded_mode),
                    degraded_mode=bool(prepared.quota_degraded_mode),
                    **_trace_safety_kwargs(prepared.safety_mode, prepared.safety_trigger_reason, []),
                ),
                metrics=TraceMetrics(
                    latency_ms=latency_ms,
                    token_in=None,
                    token_out=None,
                    model=settings.llm_model,
                    degraded=True,
                ),
            )
        )
        raise HTTPException(status_code=502, detail=llm_error_detail_for_client(e)) from e
    e2 = time.perf_counter()
    rid = cb_sink.get("request_id")
    reply = (reply_text or "").strip() if isinstance(reply_text, str) else ""
    return await finalize_chat_turn(
        prepared,
        reply=reply,
        llm_request_id=str(rid) if rid else None,
        llm_started_s=s2,
        llm_ended_s=e2,
        streamed=False,
    )
