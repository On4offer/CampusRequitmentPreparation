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
)
from app.core.settings import settings
from app.llm.client import ChatMessage, LLMClient, LLMClientError
from app.memory.stm import trim_messages_by_char_budget
from app.memory.store import session_store


router = APIRouter()    # 路由层，作用是将 API 路由注册到 FastAPI 应用实例


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
        #raise的作用是抛出一个 HTTPException 异常，状态码为 500，详情为 Missing LLM_API_KEY. Create a .env file (see .env.example).
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
    return SessionResetResponse(ok=True, existed=existed)   #对象是SessionResetResponse类的实例，ok=True表示操作成功，existed表示是否存在该会话


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

    # system 是系统提示词，用于引导 LLM 生成符合预期的回复，是一个字符串
    # 相较于Java，Python的字符串是不可变的，每次操作都会返回一个新的字符串，而不是修改原字符串
    # 声明的时候用双引号或单引号都可以，但是要保持一致
    # 不需要类型声明，Python会自动判断变量的类型
    system = (
        "你是一个温和、克制、尊重边界的情感陪伴助手。"
        "如果用户表达自伤/他伤倾向，你要进入安全模式：建议联系现实支持与专业帮助，避免给出危险建议。"
    )

    # Short-term memory: previous turns within budget (system prompt handled separately)
    # 中文版：短期记忆：预算内的前几轮（系统提示单独处理）
    # 从 session_store 取历史消息，并做 STM 裁剪（字符预算）
    # state 是一个 SessionState 类的实例，用于存储会话状态
    # session_store 是一个 InMemorySessionStore 类的实例，用于存储会话状态
    # history 是一个 ChatMessage 列表，用于存储会话历史消息
    # messages 是一个 ChatMessage 列表，用于存储 LLM 调用的消息
    state = session_store.get_or_create(user_id=user_id, session_id=session_id)
    history = trim_messages_by_char_budget(state.messages, max_chars=settings.stm_max_chars)
    messages = [ChatMessage(role="system", content=system), *history, ChatMessage(role="user", content=req.message)]

    llm = _build_llm_client()   # 从 settings 读取 LLM 配置，返回一个 LLMClient 实例
    try:
        resp = await llm.chat(messages) # 调用 LLM,await表示异步调用
    except LLMClientError as e:
        raise HTTPException(status_code=502, detail=str(e)) from e  # 502表示服务器错误，502 Bad Gateway

    reply = llm.extract_text(resp).strip()  # extract_text 从 LLM 响应中提取文本内容，strip() 去掉首尾空格
    if not reply:
        raise HTTPException(status_code=502, detail="Empty model response.")

    # Persist this turn into session memory
    # 中文版：将此转换持久化为会话内存
    # 作用：将本轮 user/assistant 消息写回 session_store，用于后续的 STM 裁剪
    session_store.append(user_id=user_id, session_id=session_id, message=ChatMessage(role="user", content=req.message))
    session_store.append(user_id=user_id, session_id=session_id, message=ChatMessage(role="assistant", content=reply))

    # latency_ms 是一个整数，用于表示 LLM 调用的延迟时间，单位是毫秒
    # 计算规则：当前时间 - 开始时间 = 延迟时间，单位是秒，乘以 1000 = 毫秒
    # perf_counter() 返回一个性能计数器的值，单位是秒，用于测量代码执行时间，记录的是此刻的时间
    latency_ms = int((time.perf_counter() - t0) * 1000)
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

