from __future__ import annotations  # 允许在函数注解中使用当前类名

"""
FastAPI 路由层（API 行为入口）。

本模块聚焦：
- /health：健康检查
- /emotion/stats：情绪日志聚合（仪表盘）
- /chat：多轮对话入口（注入 STM 历史 + 调用 LLM + 写回会话）
- /sessions：按用户列出 STM 会话；/sessions/{id}/messages 读取消息；DELETE 清空会话
- /sessions/reset：清空某个会话的短期记忆（便于演示与调试）
- /admin/eval/run、/admin/eval/jobs/{id}：异步评测跑批（运营鉴权）
"""

import asyncio
import json
import logging
import re
import time
from enum import Enum
from pathlib import Path

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse

logger = logging.getLogger(__name__)


class EmotionWindow(str, Enum):
    day = "day"
    week = "week"


from app.api.schemas import (
    AdminHotConfigPatch,
    AdminHotConfigSnapshot,
    ChatMessageOut,
    EmotionSeriesPoint,
    EmotionStatsResponse,
    EvalJobStatusResponse,
    EvalRunRequest,
    EvalRunResponse,
    ChatRequest,
    ChatResponse,
    FeedbackExportResponse,
    FeedbackItemOut,
    FeedbackListResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    LTMItemOut,
    LTMListResponse,
    LTMPatchRequest,
    LTMUndoExtractRequest,
    LTMUndoExtractResponse,
    LTMWriteRequest,
    SessionDeleteResponse,
    SessionItemOut,
    SessionListResponse,
    SessionMessagesResponse,
    UserForgetRequest,
    UserForgetResponse,
    SessionResetRequest,
    SessionResetResponse,
    TraceListResponse,
    TraceRecordOut,
    ProfileSummary,
)
from app.core.settings import settings
from app.eval.jobs import create_job, get_job, load_builtin_samples, parse_jsonl_lines, run_eval_job
from app.emotion import analyze_emotion
from app.emotion.stats import compute_emotion_stats, load_emotion_jsonl
from app.emotion.log import append_emotion_record
from app.llm.client import ChatMessage, LLMClient
from app.llm.user_visible_errors import llm_error_detail_for_client
from app.policy import decide_mode, get_system_prompt_for_mode
from app.memory.ltm import LTMItem, ltm_store
from app.memory.stm import trim_messages_by_char_budget
from app.memory.store import session_store
from app.rag import ltm_retriever
from app.rag.query_rewrite import rewrite_for_retrieval
from app.tools import execute_tool
from app.tools.router import route_tool_params
from app.trace.models import TraceDecision, TraceMetrics, TraceRecord, TraceRequest, TraceStep
from app.trace.store import FileTraceStore, InMemoryTraceStore, default_file_store, now_ms
from app.security.isolation import assert_ltm_access, assert_profile_access, assert_trace_access
from app.quota.limiter import (
    check_qps,
    check_token_budget_before_main_llm,
    consume_emotion_estimate,
    consume_main_llm_usage,
    get_daily_usage,
)
from app.safety.content_filter import merge_safety_trace_reason, sanitize_assistant_output, scan_user_input
from app.feedback.store import append_feedback_row, read_feedback_all_for_user, read_feedback_tail
from app.config.hot_config import merge_patch, snapshot_from_settings
from app.services.chat_turn import (
    finalize_chat_turn,
    iter_chat_llm_text_deltas,
    prepare_chat_until_llm,
    run_llm_chat_and_finalize,
)

router = APIRouter()    # 路由层，作用是将 API 路由注册到 FastAPI 应用实例

# Trace store（默认文件落盘；pytest 会 monkeypatch 成 InMemoryTraceStore）
# 说明：把 store 做成模块级变量，方便测试替换（避免真实写磁盘）。
trace_store = default_file_store()


def _trace_safety_kwargs(
    safety_mode: bool,
    safety_trigger_reason: str | None,
    output_filter_tags: list[str] | None,
) -> dict:
    """TraceDecision 的 safety_triggered / safety_reason（V5 内容安全可审计字段）。"""
    st, sr = merge_safety_trace_reason(
        safety_mode=safety_mode,
        safety_trigger_reason=safety_trigger_reason,
        output_filter_tags=output_filter_tags or [],
    )
    return {"safety_triggered": st, "safety_reason": sr}


def _to_trace_out(rec: TraceRecord) -> TraceRecordOut:
    """
    将内部 TraceRecord 转成 API 输出结构。

    注意：API 输出做了“拍平”，方便前端展示/调试（user_id/session_id/message 等直接在顶层）。
    """

    return TraceRecordOut(
        trace_id=rec.trace_id,
        user_id=rec.request.user_id,
        session_id=rec.request.session_id,
        message=rec.request.message,
        timestamp_ms=rec.request.timestamp_ms,
        steps=[s.model_dump() for s in rec.steps],
        decision=rec.decision.model_dump(),
        metrics=rec.metrics.model_dump(),
    )


def _build_llm_client() -> LLMClient:
    """测试 monkeypatch 入口；实现见 app.llm.factory。"""
    from app.llm.factory import build_llm_client

    return build_llm_client()


def _health_ping_redis(url: str) -> str:
    try:
        import redis

        client = redis.from_url(
            url,
            decode_responses=True,
            socket_connect_timeout=2.0,
            socket_timeout=2.0,
        )
        client.ping()
        return "ok"
    except Exception:
        return "error"


def _health_ping_database(url: str) -> None:
    from app.memory.ltm_sql import ping_database

    ping_database(url)


#这个注解的作用是将 /health 路由注册到 FastAPI 应用实例中
#get 方法用于定义一个 GET 请求，并返回一个 HealthResponse 对象。
@router.get("/health")
async def health() -> HealthResponse:   #->这个写法叫做类型注解，作用是指定函数返回值的类型
    """健康检查：存活状态；若配置了 REDIS_URL / DATABASE_URL 则返回对应探活结果。"""

    redis_st = "skipped"
    db_st = "skipped"
    ru = (settings.redis_url or "").strip()
    if ru:
        redis_st = await asyncio.to_thread(_health_ping_redis, ru)
    du = (settings.database_url or "").strip()
    if du:
        try:
            await asyncio.wait_for(asyncio.to_thread(_health_ping_database, du), timeout=8.0)
            db_st = "ok"
        except Exception:
            db_st = "error"
    return HealthResponse(
        redis=redis_st,
        database=db_st,
        ltm_extract_enabled=settings.ltm_extract_enabled,
    )


@router.get("/emotion/stats", response_model=EmotionStatsResponse)
async def emotion_stats(
    user_id: str | None = None,
    window: EmotionWindow = Query(default=EmotionWindow.week),
    max_lines: int = Query(default=4000, ge=200, le=20000),
) -> EmotionStatsResponse:
    """
    从 `emotion_log` JSONL 聚合情绪统计（日/周视图）。

    需开启 `EMOTION_LOG_ENABLED` 并有对话落盘才有数据；结果仅供产品观测，非医疗诊断。
    """
    uid = session_store.ensure_user_id(user_id)
    path = (getattr(settings, "emotion_log_path", "") or "").strip() or "data/emotion_log.jsonl"
    recs = load_emotion_jsonl(path, max_lines)
    w = "week" if window == EmotionWindow.week else "day"
    agg = compute_emotion_stats(recs, user_id=uid, window=w)
    exists = Path(path).is_file()
    hint = None
    if agg["record_count"] == 0:
        hint = "暂无数据：可在 .env 设置 EMOTION_LOG_ENABLED=true 并多轮对话后刷新。"

    return EmotionStatsResponse(
        user_id=uid,
        emotion_log_enabled=bool(getattr(settings, "emotion_log_enabled", False)),
        log_file=path,
        log_file_exists=exists,
        window=w,
        record_count=agg["record_count"],
        by_label=agg["by_label"],
        by_risk_tier=agg["by_risk_tier"],
        series=[EmotionSeriesPoint(**x) for x in agg["series"]],
        hint=hint,
    )


# post 方法用于定义一个 POST 请求，并返回一个 SessionResetResponse 对象。
@router.post("/sessions/reset")
async def session_reset(req: SessionResetRequest) -> SessionResetResponse:  
    #req表示请求体，req.user_id表示请求体中的user_id字段，->表示返回值类型
    """
    清空会话短期记忆（STM）。

    - user_id: 用户标识（空/None 会被归一为 default）
    - session_id: 会话标识（必填）
    """
    #req是SessionResetRequest类的实例，session_store是InMemorySessionStore类的实例
    user_id = session_store.ensure_user_id(req.user_id) 
    session_id = session_store.ensure_session_id(req.session_id)
    existed = session_store.reset(user_id=user_id, session_id=session_id)
    return SessionResetResponse(ok=True, existed=existed)


@router.get("/sessions", response_model=SessionListResponse)
async def list_sessions(user_id: str | None = Query(default=None, description="用户标识；空则归一为 default")) -> SessionListResponse:
    """
    列出某用户在进程内存 STM 中的会话（含消息条数）。

    说明：仅包含已产生过至少一条消息的会话；新建未发消息的会话由前端本地维护直至首轮 /chat。
    """

    uid = session_store.ensure_user_id(user_id)
    rows = session_store.list_sessions_for_user(uid)
    return SessionListResponse(
        user_id=uid,
        sessions=[SessionItemOut(session_id=sid, message_count=cnt) for sid, cnt in rows],
    )


@router.get("/sessions/{session_id}/messages", response_model=SessionMessagesResponse)
async def get_session_messages(
    session_id: str,
    user_id: str | None = Query(default=None, description="用户标识"),
) -> SessionMessagesResponse:
    """读取某会话 STM 中的消息（user/assistant），用于前端恢复聊天区。"""

    uid = session_store.ensure_user_id(user_id)
    sid = session_id.strip()
    if not sid:
        raise HTTPException(status_code=400, detail="session_id is required.")
    msgs = session_store.get_messages(user_id=uid, session_id=sid)
    if msgs is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return SessionMessagesResponse(
        user_id=uid,
        session_id=sid,
        messages=[ChatMessageOut(role=m.role, content=m.content or "") for m in msgs],
    )


@router.delete("/sessions/{session_id}", response_model=SessionDeleteResponse)
async def delete_session(
    session_id: str,
    user_id: str | None = Query(default=None, description="用户标识"),
) -> SessionDeleteResponse:
    """删除（清空）某会话的 STM，等价于 POST /sessions/reset。"""

    uid = session_store.ensure_user_id(user_id)
    sid = session_id.strip()
    if not sid:
        raise HTTPException(status_code=400, detail="session_id is required.")
    existed = session_store.reset(user_id=uid, session_id=sid)
    return SessionDeleteResponse(ok=True, existed=existed)


@router.get("/trace/{trace_id}")
async def get_trace(
    trace_id: str,
    user_id: str | None = Query(default=None, description="调用方用户；传入时须与 trace 归属一致（V5 隔离）"),
) -> TraceRecordOut:
    """
    查询单条 Trace。

    使用场景：
    - 你发起一次 /chat 后，拿到 trace_id
    - 再用该接口把“链路步骤 + 耗时 + decision/metrics”拿回来，方便演示可观测性

    V5：可传 user_id 校验归属；strict_user_isolation=true 时必须传且须匹配。
    """

    rec = trace_store.get(trace_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    assert_trace_access(rec, user_id)
    return _to_trace_out(rec)


@router.get("/traces")
async def list_traces(
    user_id: str | None = Query(default=None, description="用户标识；空则归一为 default（与 /chat 一致）"),
    session_id: str | None = Query(
        default=None,
        description="必填：会话标识。省略或仅空白将返回 400（避免误用随机 UUID 得到空列表）。",
    ),
    limit: int = Query(default=20, ge=1, le=200),
) -> TraceListResponse:
    """
    列出某个会话下最近的 Trace（用于页面/调试面板）。

    约定：
    - user_id 为空时会归一为 default（与 /chat 的逻辑一致）
    - session_id **必填且非空**；limit 默认 20
    """

    if session_id is None or not session_id.strip():
        raise HTTPException(
            status_code=400,
            detail="session_id is required (non-empty query parameter).",
        )
    uid = session_store.ensure_user_id(user_id)
    sid = session_id.strip()
    items = [_to_trace_out(x) for x in trace_store.list_by_session(user_id=uid, session_id=sid, limit=limit)]
    return TraceListResponse(items=items)


# ---------- V1: 长期记忆（LTM）占位 API ----------


@router.post("/memory/ltm")
async def post_memory_ltm(body: LTMWriteRequest) -> dict:
    """
    写入一条长期记忆（占位）。
    user_id 在 body 中；不接入 /chat 主链路，V2 再做检索与注入。
    """
    user_id = session_store.ensure_user_id(body.user_id)
    if body.type not in ("Preference", "Profile", "Event", "Constraint"):
        raise HTTPException(status_code=400, detail="type must be one of: Preference, Profile, Event, Constraint")
    ts = now_ms()
    item = LTMItem(
        id="",
        user_id=user_id,
        type=body.type,
        content=body.content,
        created_at=ts,
        source=body.source,
        confidence=body.confidence,
        tags=body.tags,
        is_active=True,
        updated_at=ts,
        embedding_status="ready",
    )
    lid = ltm_store.put(user_id, item)
    # V2：写入 LTM 后同步进检索索引，便于 /chat 召回
    item_with_id = item.model_copy(update={"id": lid})
    ltm_retriever.index_item(item_with_id)
    return {"id": lid}


@router.post("/memory/ltm/undo_extract", response_model=LTMUndoExtractResponse)
async def post_memory_ltm_undo_extract(body: LTMUndoExtractRequest) -> LTMUndoExtractResponse:
    """
    撤销某次 /chat 中隐式抽取**新建**的 LTM（Trace 里 `ltm_extract_new_ids`）。
    仅处理 source=dialogue_extract 且仍生效的条目；合并更新（update）产生的行不在此列表中。
    """
    tid = body.trace_id.strip()
    if not tid:
        raise HTTPException(status_code=400, detail="trace_id is required.")
    rec = trace_store.get(tid)
    if rec is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    assert_trace_access(rec, body.user_id)
    ids = list(rec.decision.ltm_extract_new_ids)
    owner = session_store.ensure_user_id(rec.request.user_id)
    n = 0
    for lid in ids:
        it = ltm_store.get_by_id(lid)
        if it is None or not it.is_active:
            continue
        if session_store.ensure_user_id(it.user_id) != owner:
            continue
        if (it.source or "").strip() != "dialogue_extract":
            continue
        try:
            ltm_retriever.remove_item(it)
        except Exception:
            logger.warning("undo_extract remove_item failed id=%s", lid, exc_info=True)
        if ltm_store.soft_delete(id=lid) is not None:
            n += 1
    return LTMUndoExtractResponse(trace_id=tid, deactivated=n)


@router.get("/memory/ltm")
async def get_memory_ltm(
    user_id: str | None = None,
    type: str | None = None,
    q: str | None = None,
    source: str | None = Query(default=None, description="来源精确匹配，如 dialogue_extract"),
    limit: int = Query(default=10, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
) -> LTMListResponse:
    """
    按 user_id 查询 LTM 列表，可选 type / source 过滤、q 内容包含搜索、offset/limit 分页。
    """
    uid = session_store.ensure_user_id(user_id)
    if type is not None and type not in ("Preference", "Profile", "Event", "Constraint"):
        raise HTTPException(status_code=400, detail="type must be one of: Preference, Profile, Event, Constraint")
    src_f = (source or "").strip()
    if len(src_f) > 512:
        raise HTTPException(status_code=400, detail="source filter too long (max 512).")
    rows, total = ltm_store.list_by_user(
        uid,
        type=type,
        limit=limit,
        offset=offset,
        q=q,
        only_active=True,
        source=src_f or None,
    )
    return LTMListResponse(
        items=[
            LTMItemOut(
                id=x.id,
                user_id=x.user_id,
                type=x.type,
                content=x.content,
                created_at=x.created_at,
                source=x.source,
                confidence=x.confidence,
                tags=x.tags,
                is_active=x.is_active,
                updated_at=x.updated_at,
                embedding_status=x.embedding_status,
            )
            for x in rows
        ],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.get("/memory/ltm/{id}")
async def get_memory_ltm_by_id(
    id: str,
    user_id: str | None = Query(default=None, description="调用方用户；传入时须与记忆归属一致"),
) -> LTMItemOut:
    """按 id 查询一条 LTM（仅返回生效条目）。V5：可传 user_id 校验归属。"""
    x = ltm_store.get_by_id(id)
    if x is None or not x.is_active:
        raise HTTPException(status_code=404, detail="LTM item not found.")
    assert_ltm_access(x, user_id)
    return LTMItemOut(
        id=x.id,
        user_id=x.user_id,
        type=x.type,
        content=x.content,
        created_at=x.created_at,
        source=x.source,
        confidence=x.confidence,
        tags=x.tags,
        is_active=x.is_active,
        updated_at=x.updated_at,
        embedding_status=x.embedding_status,
    )


@router.patch("/memory/ltm/{id}")
async def patch_memory_ltm(
    id: str,
    body: LTMPatchRequest,
    user_id: str | None = Query(default=None, description="调用方用户；传入时须与记忆归属一致"),
) -> LTMItemOut:
    """局部更新一条长期记忆。V5：可传 user_id 校验归属。"""
    if (
        body.content is None
        and body.tags is None
        and body.confidence is None
        and body.is_active is None
    ):
        raise HTTPException(status_code=400, detail="No fields to update.")
    existing = ltm_store.get_by_id(id)
    if existing is None:
        raise HTTPException(status_code=404, detail="LTM item not found.")
    assert_ltm_access(existing, user_id)
    updated = ltm_store.update_item(
        id=id,
        content=body.content,
        tags=body.tags,
        confidence=body.confidence,
        is_active=body.is_active,
        updated_at=now_ms(),
    )
    if updated is None:
        raise HTTPException(status_code=404, detail="LTM item not found.")
    if updated.is_active:
        ltm_retriever.index_item(updated)
    else:
        ltm_retriever.remove_item(updated)
    return LTMItemOut(
        id=updated.id,
        user_id=updated.user_id,
        type=updated.type,
        content=updated.content,
        created_at=updated.created_at,
        source=updated.source,
        confidence=updated.confidence,
        tags=updated.tags,
        is_active=updated.is_active,
        updated_at=updated.updated_at,
        embedding_status=updated.embedding_status,
    )


@router.delete("/memory/ltm/{id}")
async def delete_memory_ltm(
    id: str,
    user_id: str | None = Query(default=None, description="调用方用户；传入时须与记忆归属一致"),
) -> dict:
    """软删除一条长期记忆。V5：可传 user_id 校验归属。"""
    existing = ltm_store.get_by_id(id)
    if existing is None:
        raise HTTPException(status_code=404, detail="LTM item not found.")
    assert_ltm_access(existing, user_id)
    deleted = ltm_store.soft_delete(id=id, updated_at=now_ms())
    if deleted is None:
        raise HTTPException(status_code=404, detail="LTM item not found.")
    ltm_retriever.remove_item(deleted)
    return {"ok": True, "id": id}


@router.get("/profile/{user_id}", response_model=ProfileSummary)
async def get_profile(
    user_id: str,
    viewer_user_id: str | None = Query(
        default=None,
        description="查看者 user_id；传入或与 strict 模式下须与路径 user_id 一致",
    ),
) -> ProfileSummary:
    """
    用户画像摘要（仅聚合该 user_id 的生效 LTM）。

    V5：传 viewer_user_id 时须与路径 user_id 一致，防止越权查看他人画像。
    """
    uid = session_store.ensure_user_id(user_id)
    assert_profile_access(uid, viewer_user_id)

    all_items, total_mem = ltm_store.list_by_user(uid, limit=999_999, offset=0, only_active=True)
    by_type: dict[str, int] = {}
    for x in all_items:
        by_type[x.type] = by_type.get(x.type, 0) + 1

    snippets: list[str] = []
    for x in all_items[:5]:
        c = (x.content or "").strip()
        if len(c) > 80:
            c = c[:80] + "…"
        snippets.append(f"[{x.type}] {c}")

    return ProfileSummary(
        user_id=uid,
        total_memories=total_mem,
        by_type=by_type,
        recent_snippets=snippets,
    )


def _feedback_row_to_item(d: dict) -> FeedbackItemOut:
    return FeedbackItemOut(
        id=str(d.get("id", "")),
        trace_id=str(d.get("trace_id", "")),
        user_id=str(d.get("user_id", "")),
        rating=str(d.get("rating", "")),
        correction=d.get("correction"),
        timestamp_ms=int(d.get("timestamp_ms", 0)),
        session_id=d.get("session_id"),
    )


@router.post("/feedback", response_model=FeedbackResponse)
async def post_feedback(req: FeedbackRequest) -> FeedbackResponse:
    """
    对某轮 /chat 提交反馈（点赞/点踩/纠错）。

    - 须存在对应 trace_id，且 user_id 与 trace 归属一致（防伪造）。
    - 点踩或填写 correction 时，可按配置额外写入 `feedback_for_eval.jsonl` 供离线评测。
    """
    if not getattr(settings, "feedback_enabled", True):
        raise HTTPException(status_code=503, detail="Feedback is disabled.")

    uid = session_store.ensure_user_id(req.user_id)
    rec = trace_store.get(req.trace_id.strip())
    if rec is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    if rec.request.user_id != uid:
        raise HTTPException(status_code=403, detail="trace_id does not belong to this user_id.")

    corr = (req.correction or "").strip() or None
    mirror = bool(
        getattr(settings, "feedback_eval_mirror_enabled", True)
        and (req.rating == "dislike" or bool(corr))
    )
    eval_path = (getattr(settings, "feedback_eval_log_path", "") or "").strip() or None

    row = {
        "trace_id": req.trace_id.strip(),
        "user_id": uid,
        "session_id": rec.request.session_id,
        "rating": req.rating,
        "correction": corr,
        "timestamp_ms": now_ms(),
        "trace_message_preview": (rec.request.message or "")[:300],
        "trace_mode": rec.decision.mode,
        "trace_risk_tier": (rec.decision.emotion or {}).get("risk_tier") if rec.decision.emotion else None,
    }

    fid, mirrored = append_feedback_row(
        row,
        main_path=settings.feedback_log_path,
        eval_path=eval_path,
        mirror_to_eval=mirror,
    )
    return FeedbackResponse(ok=True, feedback_id=fid, mirrored_to_eval=mirrored)


@router.get("/feedback/recent", response_model=FeedbackListResponse)
async def list_feedback_recent(
    limit: int = Query(default=30, ge=1, le=500),
    user_id: str | None = Query(default=None, description="只看待定用户的反馈；不传则返回全局最近"),
) -> FeedbackListResponse:
    """最近反馈列表（从 JSONL 尾部读取，便于运营台/调试）。"""
    if not getattr(settings, "feedback_enabled", True):
        raise HTTPException(status_code=503, detail="Feedback is disabled.")

    uid_filter = session_store.ensure_user_id(user_id) if user_id is not None and str(user_id).strip() else None
    rows = read_feedback_tail(path=settings.feedback_log_path, limit=limit, user_id=uid_filter)
    return FeedbackListResponse(items=[_feedback_row_to_item(x) for x in rows])


@router.get("/feedback/export", response_model=FeedbackExportResponse)
async def export_feedback_jsonl(
    limit: int = Query(default=200, ge=1, le=5000),
    user_id: str | None = Query(default=None, description="只导出该用户的反馈行"),
) -> FeedbackExportResponse:
    """导出最近 N 条反馈为 JSONL 文本，便于复制到评测流水线。"""
    if not getattr(settings, "feedback_enabled", True):
        raise HTTPException(status_code=503, detail="Feedback is disabled.")

    uid_filter = session_store.ensure_user_id(user_id) if user_id is not None and str(user_id).strip() else None
    rows = read_feedback_tail(path=settings.feedback_log_path, limit=limit, user_id=uid_filter)
    lines = [json.dumps(r, ensure_ascii=False) for r in rows]
    content = "\n".join(lines) + ("\n" if lines else "")
    return FeedbackExportResponse(line_count=len(rows), content=content)


def _require_admin_config_auth(request: Request) -> None:
    """
    轻量鉴权：配置了 ADMIN_CONFIG_TOKEN 则必须带 X-Admin-Token；
    未配置时仅允许本机访问（避免公网误暴露）。
    """
    token = (getattr(settings, "admin_config_token", "") or "").strip()
    if token:
        if request.headers.get("X-Admin-Token") != token:
            raise HTTPException(status_code=401, detail="Invalid or missing X-Admin-Token")
        return
    host = (request.client.host if request.client else "") or ""
    if host in ("127.0.0.1", "::1", "localhost"):
        return
    raise HTTPException(
        status_code=403,
        detail="Admin config only from localhost, or set ADMIN_CONFIG_TOKEN and pass X-Admin-Token",
    )


@router.get("/admin/config", response_model=AdminHotConfigSnapshot)
async def get_admin_hot_config(request: Request) -> AdminHotConfigSnapshot:
    """获取当前运营热参数（白名单字段，与 data/hot_config.json 同步）。"""
    _require_admin_config_auth(request)
    return AdminHotConfigSnapshot(**snapshot_from_settings())


@router.patch("/admin/config", response_model=AdminHotConfigSnapshot)
async def patch_admin_hot_config(request: Request, body: AdminHotConfigPatch) -> AdminHotConfigSnapshot:
    """部分更新热参数：写入 hot_config.json 并立即作用于进程内 settings（下一轮 /chat 生效）。"""
    _require_admin_config_auth(request)
    patch = body.model_dump(exclude_none=True)
    if not patch:
        return AdminHotConfigSnapshot(**snapshot_from_settings())
    try:
        merge_patch(patch)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    except TypeError as e:
        raise HTTPException(status_code=400, detail=str(e)) from e
    return AdminHotConfigSnapshot(**snapshot_from_settings())


@router.get("/admin/quota")
async def get_admin_quota_snapshot(
    request: Request,
    user_id: str | None = Query(default=None, description="查看该用户的当日配额占用"),
) -> dict:
    """运营台：配额占用与当前限额配置（与内存计数器一致）。"""
    _require_admin_config_auth(request)
    uid = session_store.ensure_user_id(user_id)
    used = get_daily_usage(uid)
    lim = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
    qps = float(getattr(settings, "quota_qps_per_user", 0) or 0)
    qen = bool(getattr(settings, "quota_enabled", False))
    return {
        "user_id": uid,
        "quota_enabled": qen,
        "used_today": used,
        "limit_per_day": lim,
        "qps_per_user": qps,
    }


def _user_export_payload(uid: str) -> dict:
    """合规导出：LTM（含已软删标记）+ STM 会话 + 反馈 JSONL 中该用户行 + 摘要。"""
    items, _total = ltm_store.list_by_user(uid, limit=999_999, offset=0, only_active=False)
    ltm_out = [x.model_dump() for x in items]
    active_by_type: dict[str, int] = {}
    n_active = 0
    for x in items:
        if x.is_active:
            n_active += 1
            active_by_type[x.type] = active_by_type.get(x.type, 0) + 1
    sessions_meta = session_store.list_sessions_for_user(uid)
    stm_out: list[dict] = []
    for sid, _n in sessions_meta:
        msgs = session_store.get_messages(user_id=uid, session_id=sid)
        if msgs is None:
            continue
        stm_out.append(
            {
                "session_id": sid,
                "message_count": len(msgs),
                "messages": [{"role": m.role, "content": m.content} for m in msgs],
            }
        )
    fb_path = (getattr(settings, "feedback_log_path", "") or "").strip()
    feedback_rows = read_feedback_all_for_user(path=fb_path, user_id=uid) if fb_path else []
    q_used = get_daily_usage(uid) if getattr(settings, "quota_enabled", False) else None
    q_lim = int(getattr(settings, "quota_token_per_user_per_day", 0) or 0)
    return {
        "export_version": 1,
        "exported_at_ms": now_ms(),
        "user_id": uid,
        "profile_summary": {
            "active_ltm_count": n_active,
            "total_ltm_rows": len(items),
            "by_type_active": active_by_type,
        },
        "quota_snapshot": {
            "used_today_chars_approx": q_used,
            "limit_per_day": q_lim if q_lim > 0 else None,
        },
        "ltm": ltm_out,
        "stm_sessions": stm_out,
        "feedback": feedback_rows,
        "note": "Trace 全文未打包；可按 trace_id 单独 GET /trace/{id} 拉取（若仍存）。",
    }


@router.get("/users/{user_id}/export")
async def export_user_data_package(request: Request, user_id: str) -> JSONResponse:
    """
    运营合规：导出某用户的 LTM + STM + 反馈（JSON 附件）。
    鉴权与 /admin/config 一致。
    """
    _require_admin_config_auth(request)
    uid = session_store.ensure_user_id(user_id)
    payload = _user_export_payload(uid)
    safe = re.sub(r"[^a-zA-Z0-9._-]+", "_", uid).strip("_")[:80] or "user"
    return JSONResponse(
        content=payload,
        headers={"Content-Disposition": f'attachment; filename="user-export-{safe}.json"'},
    )


@router.post("/users/{user_id}/forget", response_model=UserForgetResponse)
async def user_forget_batch(request: Request, user_id: str, body: UserForgetRequest) -> UserForgetResponse:
    """
    运营合规：将该用户下**全部生效 LTM** 软删除并移出 RAG 索引；可选清空全部 STM。
    须 `confirm=true`（不可逆，Trace/反馈 JSONL 不自动删）。
    """
    _require_admin_config_auth(request)
    if not body.confirm:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "confirm_required",
                "message": "请设置 confirm=true 以执行遗忘（LTM 软删 + 可选清空 STM）。",
            },
        )
    uid = session_store.ensure_user_id(user_id)
    ts = now_ms()
    active_items, _ = ltm_store.list_by_user(uid, limit=999_999, offset=0, only_active=True)
    n_ltm = 0
    for it in active_items:
        deleted = ltm_store.soft_delete(id=it.id, updated_at=ts)
        if deleted:
            ltm_retriever.remove_item(deleted)
            n_ltm += 1
    n_stm = session_store.clear_all_sessions_for_user(uid) if body.clear_stm else 0
    return UserForgetResponse(ok=True, user_id=uid, ltm_deactivated=n_ltm, stm_sessions_cleared=n_stm)


def _list_recent_risk_trace_rows(*, max_items: int, max_scan_lines: int) -> tuple[list[dict], str]:
    """
    从文件 trace 索引倒序扫描，返回命中安全标记的 trace 摘要。
    返回 (items, storage_note)。
    """
    st = trace_store
    if isinstance(st, InMemoryTraceStore):
        return [], "memory_store"
    if not isinstance(st, FileTraceStore):
        return [], "unknown_store"
    idx = st.index_file
    if not idx.exists():
        return [], "file_store"
    try:
        lines = idx.read_text(encoding="utf-8").splitlines()
    except OSError:
        return [], "file_store"
    out: list[dict] = []
    scanned = 0
    for line in reversed(lines):
        if len(out) >= max_items:
            break
        if scanned >= max_scan_lines:
            break
        scanned += 1
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        tid = row.get("trace_id") or ""
        if not tid:
            continue
        rec = st.get(tid)
        if rec is None:
            continue
        d = rec.decision
        if not (d.safety_mode or d.safety_triggered):
            continue
        reason = d.safety_reason or d.safety_trigger_reason or ""
        out.append(
            {
                "trace_id": rec.trace_id,
                "user_id": rec.request.user_id,
                "session_id": rec.request.session_id,
                "timestamp_ms": rec.request.timestamp_ms,
                "safety_mode": bool(d.safety_mode),
                "safety_triggered": bool(d.safety_triggered),
                "reason": reason[:200],
                "message_preview": (rec.request.message or "")[:80],
            }
        )
    return out, "file_store"


@router.get("/admin/risk_events")
async def get_admin_risk_events(
    request: Request,
    limit: int = Query(default=25, ge=1, le=200),
    scan_lines: int = Query(default=800, ge=10, le=10000, description="最多扫描索引行数（从新到旧）"),
) -> dict:
    """运营台：最近命中安全模式/内容安全的 trace 摘要（仅文件 Trace 存储有效）。"""
    _require_admin_config_auth(request)
    items, storage = _list_recent_risk_trace_rows(max_items=limit, max_scan_lines=scan_lines)
    note = "ok"
    if storage == "memory_store":
        note = "当前为内存 Trace 存储（如 pytest），无全局风险列表；生产文件存储下可用。"
    elif storage == "unknown_store":
        note = "未知 Trace 存储实现，未扫描。"
    return {"items": items, "storage": storage, "note": note, "count": len(items)}


@router.post("/admin/eval/run", response_model=EvalRunResponse)
async def admin_eval_run(
    request: Request,
    body: EvalRunRequest,
    background_tasks: BackgroundTasks,
) -> EvalRunResponse:
    """
    启动异步评测：逐条调用与 /chat 相同的生成链路。

    需要运营鉴权（与 /admin/config 一致）。样本为 JSONL，每行 JSON 至少含 `message`。
    """
    _require_admin_config_auth(request)
    uid = session_store.ensure_user_id(body.user_id)
    if body.dataset == "builtin":
        samples = load_builtin_samples(body.limit)
        if not samples:
            raise HTTPException(
                status_code=400,
                detail="Builtin eval set missing or empty (data/eval_builtin.jsonl).",
            )
    else:
        raw = (body.jsonl or "").strip()
        if not raw:
            raise HTTPException(status_code=400, detail="jsonl is required when dataset=upload.")
        try:
            samples = parse_jsonl_lines(raw)
        except json.JSONDecodeError as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSONL: {e}") from e
    samples = samples[: body.limit]
    if not samples:
        raise HTTPException(status_code=400, detail="No samples to run.")
    job_id = create_job(samples)
    background_tasks.add_task(run_eval_job, job_id, samples, uid)
    return EvalRunResponse(job_id=job_id, total=len(samples))


@router.get("/admin/eval/jobs/{job_id}", response_model=EvalJobStatusResponse)
async def admin_eval_job_status(request: Request, job_id: str) -> EvalJobStatusResponse:
    """查询评测任务进度与结果（完成后 results 含每条的 reply/trace 或错误）。"""
    _require_admin_config_auth(request)
    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found.")
    return EvalJobStatusResponse(
        job_id=job.job_id,
        status=job.status,
        progress=job.progress,
        total=job.total,
        results=list(job.results),
        error=job.error,
        summary=job.summary,
    )


@router.post("/chat")
async def chat(req: ChatRequest) -> ChatResponse:
    """多轮对话入口（JSON 一次性返回）。"""
    prepared = await prepare_chat_until_llm(req)
    return await run_llm_chat_and_finalize(prepared)


@router.post("/chat/stream")
async def chat_stream_endpoint(req: ChatRequest) -> StreamingResponse:
    """
    SSE：data 行为 JSON。
    - meta: trace_id, user_id, session_id, quota_degraded
    - delta: 增量文本字段 c
    - done: 完整回复 + ChatResponse 字段
    - error: detail / status
    """

    async def event_gen():
        prepared = await prepare_chat_until_llm(req)
        head = {
            "event": "meta",
            "trace_id": prepared.trace_id,
            "user_id": prepared.user_id,
            "session_id": prepared.session_id,
            "quota_degraded": prepared.quota_degraded_mode,
        }
        yield f"data: {json.dumps(head, ensure_ascii=False)}\n\n"
        s2 = time.perf_counter()
        parts: list[str] = []
        meta_out: dict[str, str | None] = {}
        try:
            async for delta in iter_chat_llm_text_deltas(prepared, meta_out):
                parts.append(delta)
                yield f"data: {json.dumps({'event': 'delta', 'c': delta}, ensure_ascii=False)}\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'event': 'error', 'detail': llm_error_detail_for_client(e)}, ensure_ascii=False)}\n\n"
            return
        e2 = time.perf_counter()
        full = "".join(parts)
        try:
            out = await finalize_chat_turn(
                prepared,
                reply=full,
                llm_request_id=meta_out.get("request_id"),
                llm_started_s=s2,
                llm_ended_s=e2,
                streamed=True,
            )
            body = {"event": "done", **out.model_dump()}
            yield f"data: {json.dumps(body, ensure_ascii=False)}\n\n"
        except HTTPException as he:
            payload = {"event": "error", "status": he.status_code, "detail": he.detail}
            yield f"data: {json.dumps(payload, ensure_ascii=False, default=str)}\n\n"

    return StreamingResponse(
        event_gen(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )

