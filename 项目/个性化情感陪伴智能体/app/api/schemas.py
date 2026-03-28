from __future__ import annotations  
# __future__ 模块提供了一种方法，允许在 Python 2.x 中使用 Python 3.x 的新功能。
# annotations 是一个新的类型提示功能，用于在函数参数和返回值中指定类型。
# 作用：提高代码的可读性和可维护性，减少类型错误的发生。

"""API 层的请求/响应数据结构（Pydantic Models）。"""

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field
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
    # V3 工具：本轮工具调用摘要（工具名/状态/耗时/错误）
    tool_summary: dict | None = None
    # 二期：日配额降级省流完成本轮（与 trace.decision 一致，便于 UI 提示）
    quota_degraded: bool = False
    # V1.1：本轮隐式写入 LTM 条数（开关关或未触发为 0）
    ltm_extract_written: int = 0
    # V1.1 P1：本轮因相似而合并更新已有 LTM 条数
    ltm_extract_updated: int = 0
    # V1.1 P1：本轮抽取新建的 LTM id（可 POST /memory/ltm/undo_extract 撤销）
    ltm_extract_new_ids: list[str] = Field(default_factory=list)
    # V1.1 P2：隐式抽取已排队/后台执行（本响应中 ltm 计数可能仍为 0，稍后可 GET trace 刷新）
    ltm_extract_async_pending: bool = False


class HealthResponse(BaseModel):
    """健康检查响应体。"""

    status: str = "ok"
    # REDIS_URL / DATABASE_URL 未配置时为 skipped；配置后探活失败为 error
    redis: str = "skipped"
    database: str = "skipped"
    # V1.1：与 LTM_EXTRACT_ENABLED 一致，便于探针页/运维确认隐式记忆抽取是否开启
    ltm_extract_enabled: bool = False


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


class SessionItemOut(BaseModel):
    """会话列表单项（二期 Web：按用户列出 STM 会话）。"""

    session_id: str
    message_count: int


class SessionListResponse(BaseModel):
    """用户下会话列表。"""

    user_id: str
    sessions: list[SessionItemOut]


class ChatMessageOut(BaseModel):
    """单条对话消息（STM 只读导出）。"""

    role: str
    content: str


class SessionMessagesResponse(BaseModel):
    """某会话 STM 消息列表。"""

    user_id: str
    session_id: str
    messages: list[ChatMessageOut]


class SessionDeleteResponse(BaseModel):
    """删除会话（清空 STM）响应。"""

    ok: bool = True
    existed: bool = False


class UserForgetRequest(BaseModel):
    """运营合规：用户维度批量软删 LTM；须显式 confirm。"""

    confirm: bool = False
    clear_stm: bool = Field(default=True, description="为 True 时同时清空该用户全部 STM 会话")


class UserForgetResponse(BaseModel):
    ok: bool = True
    user_id: str
    ltm_deactivated: int
    stm_sessions_cleared: int


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


class LTMUndoExtractRequest(BaseModel):
    """按 trace_id 撤销该轮对话隐式抽取新建的 LTM（仅 source=dialogue_extract）。"""

    trace_id: str = Field(..., min_length=4, description="本轮 /chat 返回的 trace_id")
    user_id: str | None = Field(default=None, description="须与 trace 归属一致（strict 模式必填）")


class LTMUndoExtractResponse(BaseModel):
    ok: bool = True
    trace_id: str
    deactivated: int = Field(..., description="成功软删的条数")


class LTMPatchRequest(BaseModel):
    """更新一条 LTM（局部更新）。"""

    content: str | None = Field(default=None, min_length=1, description="记忆内容")
    confidence: float | None = Field(default=None, ge=0.0, le=1.0, description="置信度 0~1")
    tags: list[str] | None = Field(default=None, description="可选标签")
    is_active: bool | None = Field(default=None, description="是否生效")


class LTMListResponse(BaseModel):
    """LTM 列表响应。"""

    items: list[LTMItemOut]
    total: int = Field(default=0, description="当前筛选条件下的命中总数")
    offset: int = Field(default=0, description="本次请求的偏移")
    limit: int = Field(default=10, description="本次请求的每页条数")


# ---------- V5: 用户画像 ----------


class ProfileSummary(BaseModel):
    """用户画像摘要（仅该 user_id 的 LTM 聚合）。"""

    user_id: str
    total_memories: int
    by_type: dict[str, int] = Field(default_factory=dict, description="各类型记忆条数")
    recent_snippets: list[str] = Field(default_factory=list, description="最近几条内容摘要（截断）")


# ---------- V5: 反馈闭环 ----------


class FeedbackRequest(BaseModel):
    """对某次 /chat 的反馈（关联 trace_id）。"""

    trace_id: str = Field(..., min_length=1, description="对应 /chat 返回的 trace_id")
    user_id: str | None = Field(default=None, description="须与 trace 归属一致（归一化后与 trace 内 user_id 相同）")
    rating: Literal["like", "dislike"] = Field(..., description="点赞 / 点踩")
    correction: str | None = Field(default=None, max_length=4000, description="可选纠错或期望回复说明")


class FeedbackResponse(BaseModel):
    """反馈写入结果。"""

    ok: bool = True
    feedback_id: str
    mirrored_to_eval: bool = Field(default=False, description="是否已同步写入 feedback_for_eval.jsonl")


class FeedbackItemOut(BaseModel):
    """单条反馈（列表查询）。"""

    id: str
    trace_id: str
    user_id: str
    rating: str
    correction: str | None = None
    timestamp_ms: int = 0
    session_id: str | None = None


class FeedbackListResponse(BaseModel):
    """最近反馈列表。"""

    items: list[FeedbackItemOut]


class FeedbackExportResponse(BaseModel):
    """导出用：NDJSON 文本由接口直接返回字符串（便于复制到评测脚本）。"""

    format: Literal["jsonl"] = "jsonl"
    line_count: int
    content: str = Field(..., description="每行一个 JSON 对象")


class EvalRunRequest(BaseModel):
    """启动评测跑批：内置集或上传 JSONL。每行需含 `message` 字段。"""

    dataset: Literal["upload", "builtin"] = "upload"
    jsonl: str | None = Field(default=None, description="dataset=upload 时的原始 JSONL 文本")
    user_id: str | None = Field(default=None, description="评测用 user_id，隔离 STM/LTM")
    limit: int = Field(default=30, ge=1, le=200, description="最多跑多少条")


class EvalRunResponse(BaseModel):
    job_id: str
    total: int


class EvalJobStatusResponse(BaseModel):
    job_id: str
    status: str
    progress: int
    total: int
    results: list[dict[str, Any]] = Field(default_factory=list)
    error: str | None = None
    summary: dict[str, Any] | None = None


class EmotionSeriesPoint(BaseModel):
    bucket: str
    count: int


class EmotionStatsResponse(BaseModel):
    """情绪日志聚合（非医疗诊断，仅统计展示）。"""

    user_id: str
    emotion_log_enabled: bool
    log_file: str
    log_file_exists: bool
    window: Literal["day", "week"]
    record_count: int
    by_label: dict[str, int] = Field(default_factory=dict)
    by_risk_tier: dict[str, int] = Field(default_factory=dict)
    series: list[EmotionSeriesPoint] = Field(default_factory=list)
    disclaimer: str = Field(
        default="以下为对话情绪标签的统计展示，不构成心理健康或医学诊断；如有需要请咨询专业机构。",
        description="固定免责声明",
    )
    hint: str | None = Field(default=None, description="无数据时的引导文案")


# ---------- V5: 运营热配置（/admin/config） ----------


class AdminHotConfigSnapshot(BaseModel):
    """当前生效的运营可调参数（白名单，与 app.config.hot_config 一致）。"""

    rag_enabled: bool
    rag_top_k: int
    rag_min_score: float
    rag_max_chars: int
    rag_use_hybrid: bool
    rag_bm25_top_k: int
    rag_rewrite_enabled: bool
    rag_rewrite_min_score: float
    tool_enabled: bool
    quota_enabled: bool
    quota_token_per_user_per_day: int
    quota_qps_per_user: float
    stm_max_chars: int
    content_safety_enabled: bool
    content_safety_filter_output: bool
    feedback_enabled: bool
    quota_degrade_on_exhaust: bool
    quota_degrade_system_hint: str
    ltm_extract_enabled: bool
    ltm_extract_every_n_turns: int
    ltm_extract_dedup_enabled: bool
    ltm_extract_count_toward_quota: bool
    ltm_extract_async: bool


class AdminHotConfigPatch(BaseModel):
    """部分更新；只传需要修改的字段。"""

    model_config = ConfigDict(extra="forbid")

    rag_enabled: bool | None = None
    rag_top_k: int | None = None
    rag_min_score: float | None = None
    rag_max_chars: int | None = None
    rag_use_hybrid: bool | None = None
    rag_bm25_top_k: int | None = None
    rag_rewrite_enabled: bool | None = None
    rag_rewrite_min_score: float | None = None
    tool_enabled: bool | None = None
    quota_enabled: bool | None = None
    quota_token_per_user_per_day: int | None = None
    quota_qps_per_user: float | None = None
    stm_max_chars: int | None = None
    content_safety_enabled: bool | None = None
    content_safety_filter_output: bool | None = None
    feedback_enabled: bool | None = None
    quota_degrade_on_exhaust: bool | None = None
    quota_degrade_system_hint: str | None = None
    ltm_extract_enabled: bool | None = None
    ltm_extract_every_n_turns: int | None = None
    ltm_extract_dedup_enabled: bool | None = None
    ltm_extract_count_toward_quota: bool | None = None
    ltm_extract_async: bool | None = None

