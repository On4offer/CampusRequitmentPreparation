"""
V3 工具路由器：根据 intended_tool 与 message 提取参数。

最小版：时间类 -> time（无参或默认时区），天气类 -> weather（从消息提取城市）。
"""

from __future__ import annotations

import re
from typing import Any


# 常见城市名（可扩展）
_CITY_PATTERNS = [
    r"([\u4e00-\u9fa5]{2,10}?)(?:的?天气|天气)",
    r"天气[：:]\s*([\u4e00-\u9fa5]{2,10})",
    r"([\u4e00-\u9fa5]{2,10})(?:今天|明天)?(?:的)?天气",
]


def route_tool_params(tool_id: str, message: str) -> dict[str, Any]:
    """
    根据 tool_id 与 message 提取工具参数。

    返回参数字典，供 executor 调用。参数无效时返回空 dict 或带默认值。
    """
    msg = (message or "").strip()
    if tool_id == "time":
        # 时间工具：默认 Asia/Shanghai，可后续从消息解析时区
        return {"timezone": "Asia/Shanghai"}
    if tool_id == "weather":
        city = _extract_city(msg)
        if city:
            return {"city": city}
        # 未识别城市时用默认（北京），或由调用方决定是否拒绝
        return {"city": "北京"}
    return {}


def _extract_city(message: str) -> str | None:
    """从消息中提取城市名。"""
    for pat in _CITY_PATTERNS:
        m = re.search(pat, message)
        if m:
            return m.group(1).strip()
    # 简单兜底：消息中含"天气"时，取"天气"前的 2-10 个中文字符
    if "天气" in message:
        idx = message.find("天气")
        before = message[:idx].strip()
        # 取最后一个可能的城市名（如 "今天西安" -> 西安）
        chars = re.findall(r"[\u4e00-\u9fa5]{2,10}", before)
        if chars:
            return chars[-1]
    return None
