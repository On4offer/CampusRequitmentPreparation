"""
状态机 v0（Day5）：输出 mode（闲聊/倾听/安慰/工作）与 mode_reason。

判定依据：用户显式指令（优先）> 情绪 + 简单意图规则。
共情策略：每个 mode 对应一套 system prompt 模板（共 4 套）。
"""

from __future__ import annotations

from typing import Literal

Mode = Literal["闲聊", "倾听", "安慰", "工作"]

# 用户显式指令：命中则优先采用对应 mode
_EXPLICIT_RULES: list[tuple[tuple[str, ...], Mode, str]] = [
    (("别安慰", "不用安慰", "只想吐槽", "听我说", "别给建议"), "倾听", "用户显式希望倾听"),
    (("随便聊聊", "聊聊天", "唠唠", "没事聊聊"), "闲聊", "用户显式闲聊"),
    (("帮我", "写个", "做一下", "任务", "干活", "工作一下"), "工作", "用户提及工作/任务"),
]

# 情绪 -> 倾向的 mode（当无显式指令时）
_EMOTION_TO_MODE: list[tuple[tuple[str, ...], Mode, str]] = [
    (("低落", "焦虑", "愤怒"), "安慰", "情绪需安慰"),
    (("开心", "平静"), "闲聊", "情绪平和偏闲聊"),
    (("疲惫",), "倾听", "情绪疲惫偏倾听"),
]


def decide_mode(message: str, emotion_label: str, emotion_intensity: int) -> tuple[Mode, str]:
    """
    根据用户输入与情绪判定本次回复应采用的 mode 及原因。

    优先级：显式指令 > 情绪规则；未命中则默认 倾听。
    """
    msg = (message or "").strip()
    msg_lower = msg.lower() if msg else ""

    for keywords, mode, reason in _EXPLICIT_RULES:
        for kw in keywords:
            if kw in msg or kw in msg_lower:
                return (mode, reason)

    for labels, mode, reason in _EMOTION_TO_MODE:
        if emotion_label in labels:
            if mode == "安慰" and emotion_intensity >= 1:
                return ("安慰", reason)
            if mode == "闲聊":
                return ("闲聊", reason)
            if mode == "倾听":
                return ("倾听", reason)

    return ("倾听", "默认倾听")


# 四个 mode 对应的 system prompt 模板（共情策略骨架）
MODE_PROMPTS: dict[Mode, str] = {
    "闲聊": (
        "你是一个温和、轻松的情感陪伴助手。当前为【闲聊】模式："
        "回复可简短、自然，不必深挖，可适当接话、调侃或分享。保持边界感。"
    ),
    "倾听": (
        "你是一个温和、克制的情感陪伴助手。当前为【倾听】模式："
        "以倾听为主，少给建议，多确认与共情（如“听起来……”“这确实会……”）。"
        "用户若需要建议再给，避免抢先给方案。"
    ),
    "安慰": (
        "你是一个温和、共情的情感陪伴助手。当前为【安慰】模式："
        "先认可情绪，再轻量建议（如呼吸、休息、找人聊聊）。"
        "语气温暖但不越界，不替代专业支持。"
    ),
    "工作": (
        "你是一个情感陪伴助手。当前为【工作】模式（工具占位）："
        "用户可能提出任务类需求，后续将接入工具。此刻请简短回应并引导说明具体需求。"
    ),
}


def get_system_prompt_for_mode(mode: Mode) -> str:
    """返回指定 mode 对应的 system prompt 模板。"""
    return MODE_PROMPTS.get(mode) or MODE_PROMPTS["倾听"]
