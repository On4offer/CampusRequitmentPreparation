from __future__ import annotations

"""
V3 工具的 LangChain 封装：StructuredTool + 内部仍走 execute_tool（超时/重试与现网一致）。
策略路由（decide_mode → intended_tool）仍在链外；此处仅执行被允许的工具，不做 Agent 多轮循环。
"""

from dataclasses import dataclass
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.tools import StructuredTool

from app.tools.base import ToolError, ToolResult
from app.tools.executor import execute_tool
from app.tools.time_tool import TimeToolParams
from app.tools.weather_tool import WeatherToolParams


def _str_from_tool_result(r: ToolResult) -> str:
    if r.success and r.raw_text:
        return r.raw_text
    if r.error:
        return f"[tool_error] {r.error.message}"
    return "[tool_error] unknown"


@dataclass
class _ToolRunCapture:
    result: ToolResult | None = None
    elapsed_ms: float = 0.0


def _structured_tool_with_capture(
    tool_id: str,
    capture: _ToolRunCapture,
    *,
    timeout_s: float,
    retry_times: int,
) -> StructuredTool:
    if tool_id == "time":

        def _time_fn(timezone: str = "Asia/Shanghai") -> str:
            r, ms = execute_tool("time", {"timezone": timezone}, timeout_s=timeout_s, retry_times=retry_times)
            capture.result = r
            capture.elapsed_ms = ms
            return _str_from_tool_result(r)

        return StructuredTool.from_function(
            name="time",
            description="获取当前日期与时间（IANA 时区，默认 Asia/Shanghai）。",
            func=_time_fn,
            args_schema=TimeToolParams,
        )
    if tool_id == "weather":

        def _weather_fn(city: str) -> str:
            r, ms = execute_tool("weather", {"city": city}, timeout_s=timeout_s, retry_times=retry_times)
            capture.result = r
            capture.elapsed_ms = ms
            return _str_from_tool_result(r)

        return StructuredTool.from_function(
            name="weather",
            description="查询指定城市的天气（返回简要文本摘要）。",
            func=_weather_fn,
            args_schema=WeatherToolParams,
        )
    raise ValueError(f"unsupported tool_id for LC wrapper: {tool_id}")


def run_policy_tool_via_structured_tool(
    tool_id: str,
    params: dict[str, Any],
    *,
    timeout_s: float,
    retry_times: int,
) -> tuple[ToolResult, float]:
    """
    由策略选定的单工具执行：经 StructuredTool.invoke，仍只触发一次 execute_tool。
    """
    cap = _ToolRunCapture()
    try:
        st = _structured_tool_with_capture(tool_id, cap, timeout_s=timeout_s, retry_times=retry_times)
    except ValueError:
        return (
            ToolResult(
                success=False,
                error=ToolError(code="param_invalid", message=f"未知工具: {tool_id}"),
            ),
            0.0,
        )
    try:
        st.invoke(params)
    except Exception as e:
        return (
            ToolResult(success=False, error=ToolError(code="param_invalid", message=str(e))),
            cap.elapsed_ms,
        )
    if cap.result is None:
        return (
            ToolResult(success=False, error=ToolError(code="unknown", message="工具未返回结果")),
            cap.elapsed_ms,
        )
    return cap.result, cap.elapsed_ms


def make_lc_structured_tools_for_bind(*, timeout_s: float, retry_times: int) -> list[StructuredTool]:
    """供 ChatModel.bind_tools 使用；与上表工具名、参数模式一致（多工具绑定，仍由业务层限制实际调用）。"""

    def _time_fn(timezone: str = "Asia/Shanghai") -> str:
        r, _ = execute_tool("time", {"timezone": timezone}, timeout_s=timeout_s, retry_times=retry_times)
        return _str_from_tool_result(r)

    def _weather_fn(city: str) -> str:
        r, _ = execute_tool("weather", {"city": city}, timeout_s=timeout_s, retry_times=retry_times)
        return _str_from_tool_result(r)

    return [
        StructuredTool.from_function(
            name="time",
            description="获取当前日期与时间（IANA 时区，默认 Asia/Shanghai）。",
            func=_time_fn,
            args_schema=TimeToolParams,
        ),
        StructuredTool.from_function(
            name="weather",
            description="查询指定城市的天气。",
            func=_weather_fn,
            args_schema=WeatherToolParams,
        ),
    ]


def bind_chat_model_with_lc_tools(
    model: BaseChatModel,
    *,
    timeout_s: float,
    retry_times: int,
) -> Any:
    """返回 bind_tools 后的 Runnable；当前主链路仍预执行工具，此接口预留给受控多轮或评测。"""
    tools = make_lc_structured_tools_for_bind(timeout_s=timeout_s, retry_times=retry_times)
    return model.bind_tools(tools)
