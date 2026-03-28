"""
V3 工具基础抽象：ToolSpec、ToolResult、ToolError。

统一工具返回结构与错误码约定，便于 trace 与降级处理。
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel, Field


class ToolError(BaseModel):
    """工具执行错误（参数校验失败、超时、API 异常等）。"""

    code: str = Field(..., description="错误码：param_invalid | timeout | api_error | unknown")
    message: str = Field(..., description="人类可读错误描述")


class ToolResult(BaseModel):
    """工具执行结果（成功或失败）。"""

    success: bool = Field(..., description="是否成功")
    data: dict[str, Any] | None = Field(default=None, description="成功时的结构化数据")
    error: ToolError | None = Field(default=None, description="失败时的错误信息")
    raw_text: str | None = Field(default=None, description="可选：供 LLM 直接引用的文本摘要")


class ToolSpec(ABC):
    """
    工具规范抽象基类。

    每个工具需实现：
    - id: 工具唯一标识（如 time, weather）
    - name: 显示名称
    - run: 执行逻辑，返回 ToolResult
    """

    @property
    @abstractmethod
    def id(self) -> str:
        """工具唯一标识。"""
        ...

    @property
    @abstractmethod
    def name(self) -> str:
        """工具显示名称。"""
        ...

    @abstractmethod
    def run(self, **kwargs: Any) -> ToolResult:
        """执行工具，返回 ToolResult。"""
        ...
