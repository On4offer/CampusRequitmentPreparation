"""
V3 天气工具：查询天气（默认 mock，可切真实 API）。
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from app.tools.base import ToolResult, ToolError, ToolSpec


class WeatherToolParams(BaseModel):
    """天气工具参数。"""

    city: str = Field(..., min_length=1, max_length=50, description="城市名")


class WeatherTool(ToolSpec):
    """天气工具（V3 默认 mock）"""

    def __init__(self, *, use_mock: bool = True) -> None:
        self._use_mock = use_mock

    @property
    def id(self) -> str:
        return "weather"

    @property
    def name(self) -> str:
        return "查询天气"

    def run(self, **kwargs: Any) -> ToolResult:
        try:
            params = WeatherToolParams(**kwargs)
        except Exception as e:
            return ToolResult(
                success=False,
                error=ToolError(code="param_invalid", message=str(e)),
            )

        if self._use_mock:
            return self._mock_weather(params.city)
        # 后续可接入真实 API
        return self._mock_weather(params.city)

    def _mock_weather(self, city: str) -> ToolResult:
        """Mock 天气数据（V3 默认）。"""
        data = {
            "city": city,
            "temperature": "18°C",
            "condition": "晴",
            "humidity": "45%",
            "wind": "东风 2级",
        }
        raw_text = f"{city}：{data['condition']}，{data['temperature']}，湿度{data['humidity']}，{data['wind']}"
        return ToolResult(success=True, data=data, raw_text=raw_text)
