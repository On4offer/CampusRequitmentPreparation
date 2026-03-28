"""
V3 工具执行器与护栏：统一执行入口、超时、重试、max_steps。

V3 固定 max_steps=1（单工具调用，不做多跳 agent loop）。
"""

from __future__ import annotations

import asyncio
import concurrent.futures
import time
from typing import Any

from app.tools.base import ToolError, ToolResult
from app.tools.registry import tool_registry


def execute_tool(
    tool_id: str,
    params: dict[str, Any],
    *,
    timeout_s: float = 5.0,
    retry_times: int = 1,
) -> tuple[ToolResult, float]:
    """
    统一执行工具入口。

    返回 (ToolResult, elapsed_ms)。
    参数校验失败时直接返回错误，不重试。
    超时/API 异常时按 retry_times 重试。
    """
    tool = tool_registry.get(tool_id)
    if tool is None:
        return (
            ToolResult(
                success=False,
                error=ToolError(code="param_invalid", message=f"未注册的工具: {tool_id}"),
            ),
            0.0,
        )

    elapsed_ms = 0.0
    last_error: ToolError | None = None

    for attempt in range(retry_times + 1):
        start = time.perf_counter()
        try:
            # 在线程池中执行，避免阻塞主线程
            with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
                future = ex.submit(tool.run, **params)
                result = future.result(timeout=timeout_s)
            elapsed_ms = (time.perf_counter() - start) * 1000
            if result.success:
                return result, elapsed_ms
            last_error = result.error
            return result, elapsed_ms
        except concurrent.futures.TimeoutError:
            elapsed_ms = (time.perf_counter() - start) * 1000
            last_error = ToolError(code="timeout", message=f"工具执行超时 ({timeout_s}s)")
            if attempt < retry_times:
                continue
            return (
                ToolResult(success=False, error=last_error),
                elapsed_ms,
            )
        except Exception as e:
            elapsed_ms = (time.perf_counter() - start) * 1000
            last_error = ToolError(code="api_error", message=str(e))
            if attempt < retry_times:
                continue
            return (
                ToolResult(success=False, error=last_error),
                elapsed_ms,
            )

    return (
        ToolResult(success=False, error=last_error or ToolError(code="unknown", message="未知错误")),
        elapsed_ms,
    )


async def execute_tool_async(
    tool_id: str,
    params: dict[str, Any],
    *,
    timeout_s: float = 5.0,
    retry_times: int = 1,
) -> tuple[ToolResult, float]:
    """
    异步执行工具（内部用线程池执行同步 run）。
    """
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(
        None,
        lambda: execute_tool(tool_id, params, timeout_s=timeout_s, retry_times=retry_times),
    )
