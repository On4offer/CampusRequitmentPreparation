from __future__ import annotations  # 允许在函数注解中使用当前类名

"""
FastAPI 路由层（API 行为入口）。

本模块聚焦：
- /health：健康检查
- /chat：多轮对话入口（注入 STM 历史 + 调用 LLM + 写回会话）
- /sessions/reset：清空某个会话的短期记忆（便于演示与调试）
"""

import time
import uuid

from fastapi import APIRouter, HTTPException

from app.api.schemas import (
    ChatRequest,
    ChatResponse,
    HealthResponse,
    SessionResetRequest,
    SessionResetResponse,
    TraceListResponse,
    TraceRecordOut,
)
from app.core.settings import settings
from app.emotion import analyze_emotion
from app.llm.client import ChatMessage, LLMClient, LLMClientError
from app.policy import decide_mode, get_system_prompt_for_mode
from app.memory.stm import trim_messages_by_char_budget
from app.memory.store import session_store
from app.trace.models import TraceDecision, TraceMetrics, TraceRecord, TraceRequest, TraceStep
from app.trace.store import InMemoryTraceStore, default_file_store, now_ms

# Day4：安全模式时的系统提示（更克制、强调专业支持）
SAFE_SYSTEM_PROMPT = (
    "你处于安全模式。用户可能表达了自伤或他伤相关想法。"
    "你必须：表达关心、建议联系现实中的亲友或专业心理/医疗支持，不要追问细节，不要给出任何可能加重风险的建议。"
    "回复简短、温和、明确导向寻求专业帮助。"
)
DEFAULT_SYSTEM_PROMPT = (
    "你是一个温和、克制、尊重边界的情感陪伴助手。"
    "如果用户表达自伤/他伤倾向，你要进入安全模式：建议联系现实支持与专业帮助，避免给出危险建议。"
)


router = APIRouter()    # 路由层，作用是将 API 路由注册到 FastAPI 应用实例

# Trace store（默认文件落盘；pytest 会 monkeypatch 成 InMemoryTraceStore）
# 说明：把 store 做成模块级变量，方便测试替换（避免真实写磁盘）。
trace_store = default_file_store()


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


# 助手函数：构造 LLMClient，作用是从 settings 读取 LLM 配置并创建 LLMClient 实例
def _build_llm_client() -> LLMClient:
    """
    构造 LLMClient（从 settings 读取 base_url/key/model 等配置）。

    注意：
    - 若未配置 key，会返回 500 并提示如何配置 `.env`
    - 测试中会 monkeypatch 此函数以 mock 掉真实网络调用
    """

    # 从 settings 读取 LLM 配置
    if not settings.llm_api_key:
        # 若未配置 LLM_API_KEY，返回 500 并提示如何配置 .env
        raise HTTPException(
            status_code=500,
            detail="Missing LLM_API_KEY. Create a .env file (see .env.example).",
        )
    # 若配置了 LLM_API_KEY，返回 LLMClient 实例
    return LLMClient(
        base_url=settings.llm_base_url, # 从 settings 读取 LLM base_url
        api_key=settings.llm_api_key, # 从 settings 读取 LLM api_key
        model=settings.llm_model, # 从 settings 读取 LLM model
        timeout_s=settings.llm_timeout_s,
    )


#这个注解的作用是将 /health 路由注册到 FastAPI 应用实例中
#get 方法用于定义一个 GET 请求，并返回一个 HealthResponse 对象。
@router.get("/health")
async def health() -> HealthResponse:   #->这个写法叫做类型注解，作用是指定函数返回值的类型
    """健康检查：用于判断服务是否存活。"""

    return HealthResponse()


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


@router.get("/trace/{trace_id}")
async def get_trace(trace_id: str) -> TraceRecordOut:
    """
    查询单条 Trace。

    使用场景：
    - 你发起一次 /chat 后，拿到 trace_id
    - 再用该接口把“链路步骤 + 耗时 + decision/metrics”拿回来，方便演示可观测性
    """

    rec = trace_store.get(trace_id)
    if rec is None:
        raise HTTPException(status_code=404, detail="Trace not found.")
    return _to_trace_out(rec)


@router.get("/traces")
async def list_traces(user_id: str | None = None, session_id: str | None = None, limit: int = 20) -> TraceListResponse:
    """
    列出某个会话下最近的 Trace（用于页面/调试面板）。

    约定：
    - user_id 为空时会归一为 default（与 /chat 的逻辑一致）
    - session_id 必填；limit 默认 20
    """

    uid = session_store.ensure_user_id(user_id)
    sid = session_store.ensure_session_id(session_id)
    items = [_to_trace_out(x) for x in trace_store.list_by_session(user_id=uid, session_id=sid, limit=limit)]
    return TraceListResponse(items=items)


@router.post("/chat")
# 这个方法的req是ChatRequest类的实例，session_store是InMemorySessionStore类的实例
# 作用域：async def 表示这是一个异步方法，作用域是整个方法体
# req 只作用于当前请求，不会影响其他请求，就是只影响当前方法的作用域
async def chat(req: ChatRequest) -> ChatResponse:
    """
    多轮对话入口（Day1/Day2 主入口）。

    核心流程：
    1) 规范化 user_id/session_id
    2) 从 session_store 取历史消息，并做 STM 裁剪（字符预算）
    3) 拼接 system + history + 本轮 user 消息，调用 LLM
    4) 将本轮 user/assistant 消息写回 session_store
    5) 返回 reply/trace_id/user_id/session_id
    """

    t0 = time.perf_counter()    # time是python内置的模块，用于处理时间，perf_counter()返回一个性能计数器的值，单位是秒
    trace_id = str(uuid.uuid4())    # trace_id 是一个唯一标识符，用于跟踪请求的生命周期
    user_id = session_store.ensure_user_id(req.user_id) # req的全拼是request
    session_id = session_store.ensure_session_id(req.session_id)

    # Day3: trace 记录的“步骤列表”。我们会把关键步骤的起止时间打点写进去。
    steps: list[TraceStep] = []
    request_ts = now_ms()

    # Day4: 情绪识别（LLM 为主、关键词兜底）；风险分层仍用关键词。需先有 llm 再调用。
    llm = _build_llm_client()
    emotion_result = await analyze_emotion(req.message, llm=llm)
    safety_mode = emotion_result.risk_tier == "高风险"
    safety_trigger_reason = emotion_result.evidence if safety_mode else None
    # Day5: 状态机输出 mode + mode_reason；高风险强制倾听，关注档优先倾听
    mode, mode_reason = decide_mode(req.message, str(emotion_result.label), emotion_result.intensity)
    if safety_mode:
        mode, mode_reason = "倾听", "高风险安全模式优先倾听"
    elif emotion_result.risk_tier == "关注":
        mode, mode_reason = "倾听", "关注档优先倾听"
    system = SAFE_SYSTEM_PROMPT if safety_mode else get_system_prompt_for_mode(mode)
    emotion_for_trace = {
        "label": emotion_result.label,
        "intensity": emotion_result.intensity,
        "evidence": emotion_result.evidence,
        "risk_tier": emotion_result.risk_tier,
    }

    def _mark_step(name: str, start_ms: int, end_ms: int, *, input_summary: str | None = None, output_summary: str | None = None, error: str | None = None) -> None:
        # 这里做成内部函数：减少重复代码，也更容易给你看清楚“结构是什么、如何复用”
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

    # system：安全模式用 SAFE_SYSTEM_PROMPT，否则用状态机 mode 对应的 prompt 模板（Day5）

    # Short-term memory: previous turns within budget (system prompt handled separately)
    # 中文版：短期记忆：预算内的前几轮（系统提示单独处理）
    # 从 session_store 取历史消息，并做 STM 裁剪（字符预算）
    # state 是一个 SessionState 类的实例，用于存储会话状态
    # session_store 是一个 InMemorySessionStore 类的实例，用于存储会话状态
    # history 是一个 ChatMessage 列表，用于存储会话历史消息
    # messages 是一个 ChatMessage 列表，用于存储 LLM 调用的消息
    # Step1: load_session + trim_stm
    s1 = time.perf_counter()
    state = session_store.get_or_create(user_id=user_id, session_id=session_id)
    history = trim_messages_by_char_budget(state.messages, max_chars=settings.stm_max_chars)
    messages = [ChatMessage(role="system", content=system), *history, ChatMessage(role="user", content=req.message)]
    e1 = time.perf_counter()
    _mark_step(
        "load_session_and_trim_stm",
        start_ms=int((s1 - t0) * 1000),
        end_ms=int((e1 - t0) * 1000),
        input_summary=f"history_before={len(state.messages)} max_chars={settings.stm_max_chars}",
        output_summary=f"history_after={len(history)} messages_for_llm={len(messages)}",
    )

    # Step2: llm_call（复用上面为情绪识别已构建的 llm）
    s2 = time.perf_counter()
    try:
        resp = await llm.chat(messages) # 调用 LLM,await表示异步调用
    except LLMClientError as e:
        e2 = time.perf_counter()
        _mark_step(
            "llm_call",
            start_ms=int((s2 - t0) * 1000),
            end_ms=int((e2 - t0) * 1000),
            input_summary=f"messages={len(messages)} model={settings.llm_model}",
            error=str(e),
        )
        # 把失败 trace 也落盘（排障更友好）
        latency_ms = int((time.perf_counter() - t0) * 1000)
        trace_store.put(
            TraceRecord(
                trace_id=trace_id,
                request=TraceRequest(user_id=user_id, session_id=session_id, message=req.message, timestamp_ms=request_ts),
                steps=steps,
                decision=TraceDecision(emotion=emotion_for_trace, mode=mode, mode_reason=mode_reason, safety_mode=safety_mode, safety_trigger_reason=safety_trigger_reason),
                metrics=TraceMetrics(latency_ms=latency_ms, token_in=None, token_out=None, model=settings.llm_model, degraded=True),
            )
        )
        raise HTTPException(status_code=502, detail=str(e)) from e  # 502表示服务器错误，502 Bad Gateway
    e2 = time.perf_counter()
    _mark_step(
        "llm_call",
        start_ms=int((s2 - t0) * 1000),
        end_ms=int((e2 - t0) * 1000),
        input_summary=f"messages={len(messages)} model={settings.llm_model}",
        output_summary=f"llm_request_id={resp.get('request_id')}",
    )

    reply = llm.extract_text(resp).strip()  # extract_text 从 LLM 响应中提取文本内容，strip() 去掉首尾空格
    if not reply:
        # 空响应也记录 trace（便于定位“模型成功返回，但结构异常/为空”的情况）
        latency_ms = int((time.perf_counter() - t0) * 1000)
        _mark_step("extract_text", start_ms=latency_ms, end_ms=latency_ms, error="empty_reply")
        trace_store.put(
            TraceRecord(
                trace_id=trace_id,
                request=TraceRequest(user_id=user_id, session_id=session_id, message=req.message, timestamp_ms=request_ts),
                steps=steps,
                decision=TraceDecision(emotion=emotion_for_trace, mode=mode, mode_reason=mode_reason, safety_mode=safety_mode, safety_trigger_reason=safety_trigger_reason),
                metrics=TraceMetrics(latency_ms=latency_ms, token_in=None, token_out=None, model=settings.llm_model, degraded=True),
            )
        )
        raise HTTPException(status_code=502, detail="Empty model response.")

    # Persist this turn into session memory
    # 中文版：将此转换持久化为会话内存
    # 作用：将本轮 user/assistant 消息写回 session_store，用于后续的 STM 裁剪
    s3 = time.perf_counter()
    session_store.append(user_id=user_id, session_id=session_id, message=ChatMessage(role="user", content=req.message))
    session_store.append(user_id=user_id, session_id=session_id, message=ChatMessage(role="assistant", content=reply))
    e3 = time.perf_counter()
    _mark_step(
        "persist_memory",
        start_ms=int((s3 - t0) * 1000),
        end_ms=int((e3 - t0) * 1000),
        output_summary="appended user+assistant messages to session_store",
    )

    # latency_ms 是一个整数，用于表示 LLM 调用的延迟时间，单位是毫秒
    # 计算规则：当前时间 - 开始时间 = 延迟时间，单位是秒，乘以 1000 = 毫秒
    # perf_counter() 返回一个性能计数器的值，单位是秒，用于测量代码执行时间，记录的是此刻的时间
    latency_ms = int((time.perf_counter() - t0) * 1000)

    # Day3: 生成 trace record 并落盘
    # token_in/token_out：这里先用“字符长度近似”做个占位（后续可替换成真实 token 计数）
    token_in_est = sum(len(m.content or "") for m in messages)
    token_out_est = len(reply)
    trace_store.put(
        TraceRecord(
            trace_id=trace_id,
            request=TraceRequest(user_id=user_id, session_id=session_id, message=req.message, timestamp_ms=request_ts),
            steps=steps,
            decision=TraceDecision(
                emotion=emotion_for_trace,
                mode=mode,
                mode_reason=mode_reason,
                safety_mode=safety_mode,
                safety_trigger_reason=safety_trigger_reason,
            ),
            metrics=TraceMetrics(
                latency_ms=latency_ms,
                token_in=token_in_est,
                token_out=token_out_est,
                model=settings.llm_model,
                degraded=False,
            ),
        )
    )

    debug = None    # debug 是一个字典，用于返回额外的调试信息
    # 作用：在开发环境下，返回额外的调试信息，用于排查问题
    if settings.debug:
        debug = {
            "trace_id": trace_id,
            "latency_ms": latency_ms,
            "llm_request_id": resp.get("request_id"),
            "model": settings.llm_model,
            "user_id": user_id,
            "session_id": session_id,
            "history_messages": len(history),
        }

    # 返回 ChatResponse 类的实例，用于返回给客户端
    # 作用：将 reply/trace_id/user_id/session_id/debug 封装成一个对象，方便客户端处理
    return ChatResponse(reply=reply, trace_id=trace_id, user_id=user_id, session_id=session_id, debug=debug)

