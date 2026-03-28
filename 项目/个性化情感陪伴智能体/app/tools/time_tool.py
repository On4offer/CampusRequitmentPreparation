"""
V3 时间工具：获取当前时间/日期。
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from app.tools.base import ToolResult, ToolError, ToolSpec


class TimeToolParams(BaseModel):
    """时间工具参数（可选时区）。"""

    timezone: str = Field(default="Asia/Shanghai", description="时区，如 Asia/Shanghai")


class TimeTool(ToolSpec):
    """时间工具"""

    @property
    def id(self) -> str:
        return "time"

    @property
    def name(self) -> str:
        return "获取当前时间"

    def run(self, **kwargs: Any) -> ToolResult:
        try:
            params = TimeToolParams(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=ToolError(code="param_invalid", message=str(e)),
            )

        try:
            tz = ZoneInfo(params.timezone)
        except Exception:
            return ToolResult(
                success=False,
                error=ToolError(code="param_invalid", message=f"无效时区: {params.timezone}"),
            )

        now = datetime.now(tz)
        data = {
            "datetime": now.strftime("%Y-%m-%d %H:%M:%S"),
            "date": now.strftime("%Y-%m-%d"),
            "time": now.strftime("%H:%M:%S"),
            "timezone": params.timezone,
        }
        raw_text = f"当前时间：{data['datetime']}（{params.timezone}）"
        return ToolResult(success=True, data=data, raw_text=raw_text)
