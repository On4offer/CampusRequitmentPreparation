"""
V3 工具系统：工具注册、路由、执行与护栏。

导出：
- tool_registry: 工具注册中心单例
- ToolSpec, ToolResult, ToolError: 基础抽象
- execute_tool: 统一执行入口
"""

from __future__ import annotations

from app.tools.base import ToolError, ToolResult, ToolSpec
from app.tools.registry import tool_registry
from app.tools.executor import execute_tool
from app.tools.time_tool import TimeTool
from app.tools.weather_tool import WeatherTool

# 注册内置工具
tool_registry.register(TimeTool())
tool_registry.register(WeatherTool(use_mock=True))

__all__ = [
    "ToolSpec",
    "ToolResult",
    "ToolError",
    "tool_registry",
    "execute_tool",
]
