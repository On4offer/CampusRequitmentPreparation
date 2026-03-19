from __future__ import annotations  
# __future__ 模块提供了一种方法，允许在 Python 2.x 中使用 Python 3.x 的新功能。
# annotations 是一个新的类型提示功能，用于在函数参数和返回值中指定类型。
# 作用：提高代码的可读性和可维护性，减少类型错误的发生。

"""API 层的请求/响应数据结构（Pydantic Models）。"""

from pydantic import BaseModel, Field
# pydantic 是一个用于数据验证和序列化的 Python 库。
# 作用：定义数据模型，自动验证数据，将数据转换为 Python 对象，将 Python 对象转换为 JSON 字符串。
# BaseModel 是 pydantic 的核心类，用于定义数据模型。Field 是 pydantic 的字段类，用于定义数据模型的字段。


# ChatRequest是一个类，用于定义聊天接口的请求体。
class ChatRequest(BaseModel):
    """聊天接口请求体。"""

    message: str = Field(..., min_length=1, max_length=8000)
    # message 是聊天接口的请求参数，用于传递用户的消息。
    # 作用：将用户的消息传递给后端，后端根据消息生成回复。
    # 约束：必须是一个非空字符串，长度必须在 1 到 8000 之间。
    user_id: str | None = None
    # user_id 是聊天接口的请求参数，用于标识用户。
    # 作用：将用户的消息与用户进行关联，方便后端根据用户进行个性化回复。
    # 约束：可以为空字符串，长度无限制。
    session_id: str | None = None
    # session_id 是聊天接口的请求参数，用于标识会话。
    # 作用：将用户的消息与会话进行关联，方便后端根据会话进行上下文理解。
    # 约束：可以为空字符串，长度无限制。


class ChatResponse(BaseModel):
    """聊天接口响应体。"""

    reply: str
    trace_id: str
    user_id: str
    session_id: str
    debug: dict | None = None
    # V2 RAG：本轮引用的记忆（id/type/score）
    citations: list | None = None


class HealthResponse(BaseModel):
    """健康检查响应体。"""

    status: str = "ok"


class SessionResetRequest(BaseModel):
    """会话清空请求体：清空某个 user_id + session_id 的短期记忆。"""

    user_id: str | None = None
    # user_id 是会话清空接口的请求参数，用于标识用户。
    # 作用：将会话清空操作与用户进行关联，方便后端根据用户进行会话清空。
    # 约束：可以为空字符串，长度无限制。
    session_id: str | None = None
    # session_id 是会话清空接口的请求参数，用于标识会话。
    # 作用：将会话清空操作与会话进行关联，方便后端根据会话进行会话清空。
    # 约束：可以为空字符串，长度无限制。


class SessionResetResponse(BaseModel):
    """会话清空响应体：existed 表示清空前该会话是否存在。"""

    ok: bool = True
    # ok 是会话清空接口的响应参数，用于表示会话清空操作是否成功。
    # 作用：告诉客户端会话清空操作是否成功。
    # 约束：必须是一个布尔值，True 表示成功，False 表示失败。
    existed: bool = False
    # existed 是会话清空接口的响应参数，用于表示清空前该会话是否存在。
    # 作用：告诉客户端清空前该会话是否存在，方便客户端根据情况进行处理。
    # 约束：必须是一个布尔值，True 表示存在，False 表示不存在。


# ---------- Day3: Trace（可观测性） ----------


class TraceStepOut(BaseModel):
    """Trace 的 step 输出结构（API 返回用）。"""

    name: str
    start_ms: int
    end_ms: int
    input_summary: str | None = None
    output_summary: str | None = None
    error: str | None = None


class TraceRecordOut(BaseModel):
    """单条 Trace 记录输出结构。"""

    trace_id: str
    user_id: str
    session_id: str
    message: str
    timestamp_ms: int
    steps: list[TraceStepOut]
    decision: dict
    metrics: dict


class TraceListResponse(BaseModel):
    """某会话下 Trace 列表响应。"""

    items: list[TraceRecordOut]


# ---------- V1: 长期记忆（LTM）占位 ----------


class LTMWriteRequest(BaseModel):
    """写入一条 LTM 的请求体。"""

    user_id: str = Field(default="default", description="所属用户")
    type: str = Field(..., description="Preference | Profile | Event | Constraint")
    content: str = Field(..., min_length=1, description="记忆内容")
    source: str = Field(default="", description="来源")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度 0~1")
    tags: list[str] = Field(default_factory=list, description="可选标签")


class LTMItemOut(BaseModel):
    """单条 LTM 输出（API 返回）。"""

    id: str
    user_id: str
    type: str
    content: str
    created_at: int
    source: str
    confidence: float
    tags: list[str]
    is_active: bool
    updated_at: int
    embedding_status: str


class LTMPatchRequest(BaseModel):
    """更新一条 LTM（局部更新）。"""

    content: str | None = Field(default=None, min_length=1, description="记忆内容")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="置信度 0~1")
    tags: list[str] | None = Field(default=None, description="可选标签")
    is_active: bool | None = Field(default=None, description="是否生效")


class LTMListResponse(BaseModel):
    """LTM 列表响应。"""

    items: list[LTMItemOut]

