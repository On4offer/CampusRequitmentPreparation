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

