"""
V3 工具注册中心：注册、查询、卸载。

未注册工具调用时返回结构化错误。
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from app.tools.base import ToolSpec

if TYPE_CHECKING:
    pass


class ToolRegistry:
    """工具注册中心。"""

    def __init__(self) -> None:
        self._tools: dict[str, ToolSpec] = {}

    def register(self, tool: ToolSpec) -> None:
        """注册工具。"""
        self._tools[tool.id] = tool

    def get(self, tool_id: str) -> ToolSpec | None:
        """按 id 查询工具。"""
        return self._tools.get(tool_id)

    def unregister(self, tool_id: str) -> bool:
        """卸载工具，返回是否成功。"""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def list_tools(self) -> list[str]:
        """返回已注册工具 id 列表。"""
        return list(self._tools.keys())


# 模块级单例
tool_registry = ToolRegistry()
