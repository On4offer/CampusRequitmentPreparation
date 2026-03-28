from __future__ import annotations

"""
Trace 数据结构定义（用于“可观测 + 可回放”）。

设计目标：
- 让每次 /chat 请求都可以“回放链路”：到底走了哪些步骤、每步耗时多少、输入输出摘要是什么
- 为后续 Day4/Day5（情绪识别/状态机）预留 decision 字段
- 为后续成本治理预留 token_in/token_out（当前可先用估算）
"""

from pydantic import BaseModel, Field


class TraceStep(BaseModel):
    """一次请求中的某个步骤（step）。"""

    name: str = Field(..., description="步骤名称，如 load_session/trim_stm/llm_call/persist_memory")
    start_ms: int = Field(..., description="相对请求开始的起始时间（ms）")
    end_ms: int = Field(..., description="相对请求开始的结束时间（ms）")
    input_summary: str | None = Field(default=None, description="输入摘要（可选，避免写入敏感信息）")
    output_summary: str | None = Field(default=None, description="输出摘要（可选）")
    error: str | None = Field(default=None, description="该步骤错误信息（可选）")


class TraceRequest(BaseModel):
    """请求侧信息（便于定位是哪位用户、哪段会话、问了什么）。"""

    user_id: str
    session_id: str
    message: str
    timestamp_ms: int


class TraceDecision(BaseModel):
    """决策信息（为情绪识别/状态机做占位）。"""

    emotion: dict | None = None
    mode: str | None = None
    mode_reason: str | None = None
    safety_mode: bool | None = None
    safety_trigger_reason: str | None = None  # Day4：触发安全模式的原因（如命中关键词）
    # V5：可审计总览（含输出脱敏等）；与 safety_trigger_reason 并存
    safety_triggered: bool | None = None
    safety_reason: str | None = None
    # V1 工具占位：mode=工具 时填写，便于 V3 真实接入
    intended_tool: str | None = None  # 如 weather / memo / time / unknown
    tool_params_placeholder: dict | None = None
    # V3 工具执行：实际选中的工具、状态、错误
    tool_selected: str | None = None  # 实际调用的工具 id
    tool_status: str | None = None  # success | failed | skipped
    tool_error: str | None = None  # 失败时的错误信息
    # V2 RAG：本轮命中的长期记忆 id/type/score
    memory_hits: list | None = None  # [{"id": str, "type": str, "score": float}, ...]
    # V5 配额：日预算字符量（近似 token）、上限、是否超额拒绝
    quota_used_today: int | None = None
    quota_limit: int | None = None
    quota_exceeded: bool | None = None
    # 二期：日配额触顶后走「省流」成功完成本轮时为 True；纯 429 拒绝为 False/None
    degraded_mode: bool | None = None
    # V1.1：本轮对话隐式 LTM 写入条数（未开启或未触发为 0）
    ltm_extract_written: int | None = None
    # V1.1 P1：本轮因去重而合并更新的已有 LTM 条数
    ltm_extract_updated: int | None = None
    # V1.1 P1：本轮抽取**新建**的 LTM id（非 merge）；供 undo_extract 软删
    ltm_extract_new_ids: list[str] = Field(default_factory=list)


class TraceMetrics(BaseModel):
    """度量信息（耗时/成本/模型等）。"""

    latency_ms: int
    token_in: int | None = None
    token_out: int | None = None
    model: str | None = None
    degraded: bool | None = None


class TraceRecord(BaseModel):
    """一次请求的完整 trace 记录。"""

    trace_id: str
    request: TraceRequest
    steps: list[TraceStep]
    decision: TraceDecision
    metrics: TraceMetrics

