"""
状态机 v0（Day5）/ V1 可配置：输出 mode（闲聊/倾听/安慰/工作）与 mode_reason。

判定依据：用户显式指令（优先）> 情绪 + 简单意图规则。
共情策略：每个 mode 对应一套 system prompt 模板；支持从配置文件加载（V1）。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Literal

Mode = Literal["闲聊", "倾听", "安慰", "工作", "工具"]

# ---------- 代码内默认（无配置文件或加载失败时使用） ----------

# V1：工具意图优先于显式指令（关键词命中则 mode=工具，并给出 intended_tool）
_TOOL_KEYWORDS: list[tuple[tuple[str, ...], str, str]] = [
    (("天气", "查天气", "天气怎么样", "明天天气"), "weather", "用户请求查天气"),
    (("记一下", "备忘", "提醒", "记个事", "记一件事"), "memo", "用户请求备忘/提醒"),
    (("几点了", "现在几点", "今天几号", "时间"), "time", "用户请求时间"),
]

_DEFAULT_EXPLICIT_RULES: list[tuple[tuple[str, ...], Mode, str]] = [
    (("别安慰", "不用安慰", "只想吐槽", "听我说", "别给建议"), "倾听", "用户显式希望倾听"),
    (("随便聊聊", "聊聊天", "唠唠", "没事聊聊"), "闲聊", "用户显式闲聊"),
    (("帮我", "写个", "做一下", "任务", "干活", "工作一下"), "工作", "用户提及工作/任务"),
]

_DEFAULT_EMOTION_TO_MODE: list[tuple[tuple[str, ...], Mode, str]] = [
    (("低落", "焦虑", "愤怒"), "安慰", "情绪需安慰"),
    (("开心", "平静"), "闲聊", "情绪平和偏闲聊"),
    (("疲惫",), "倾听", "情绪疲惫偏倾听"),
]

_DEFAULT_MODE_PROMPTS: dict[Mode, str] = {
    "闲聊": (
        "你是一个温和、轻松的情感陪伴助手。当前为【闲聊】模式："
        "回复可简短、自然，不必深挖，可适当接话、调侃或分享。保持边界感。"
    ),
    "倾听": (
        "你是一个温和、克制的情感陪伴助手。当前为【倾听】模式："
        "以倾听为主，少给建议，多确认与共情（如「听起来……」「这确实会……」）。"
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
    "工具": (
        "你是一个情感陪伴助手。当前为【工具】模式（占位）："
        "用户可能请求查天气、记备忘、查时间等，后续将接入真实工具。此刻请简短回应并说明「该能力即将上线」。"
    ),
}

# 外部配置（由 reload_policy_config 填充；None 表示使用上述默认）
_policy_config: dict[str, Any] | None = None


def reload_policy_config(config_path: str | Path | None) -> None:
    """
    从 JSON 文件加载共情策略配置；空路径或文件不存在时使用代码内默认。
    约定：config_path 为绝对路径或相对于当前工作目录；配置文件格式见 config/policy_config.json。
    """
    global _policy_config
    if not config_path:
        _policy_config = None
        return
    p = Path(config_path)
    if not p.is_absolute():
        p = Path.cwd() / p
    if not p.exists():
        _policy_config = None
        return
    try:
        raw = p.read_text(encoding="utf-8")
        _policy_config = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        _policy_config = None


def decide_mode(
    message: str, emotion_label: str, emotion_intensity: int
) -> tuple[Mode, str, str | None, dict | None]:
    """
    根据用户输入与情绪判定本次回复应采用的 mode 及原因。
    优先级：工具关键词 > 显式指令 > 情绪规则；未命中则默认 倾听。
    当 mode=工具 时，返回 (mode, reason, intended_tool, tool_params_placeholder)；否则后两者为 None。
    """
    msg = (message or "").strip()
    msg_lower = msg.lower() if msg else ""

    # 1) 工具意图（V1 占位：关键词 -> 工具 mode + intended_tool）
    for keywords, tool_id, reason in _TOOL_KEYWORDS:
        for kw in keywords:
            if kw in msg or kw in msg_lower:
                return ("工具", reason, tool_id, {})

    # 2) 显式指令
    if _policy_config and "explicit_rules" in _policy_config:
        for rule in _policy_config["explicit_rules"]:
            for kw in rule.get("keywords") or []:
                if kw in msg or kw in msg_lower:
                    return (rule["mode"], rule.get("reason", ""), None, None)
    else:
        for keywords, mode, reason in _DEFAULT_EXPLICIT_RULES:
            for kw in keywords:
                if kw in msg or kw in msg_lower:
                    return (mode, reason, None, None)

    # 3) 情绪规则
    if _policy_config and "emotion_to_mode" in _policy_config:
        for rule in _policy_config["emotion_to_mode"]:
            if emotion_label in (rule.get("emotion_labels") or []):
                min_i = rule.get("min_intensity", 0)
                if emotion_intensity >= min_i:
                    return (rule["mode"], rule.get("reason", ""), None, None)
    else:
        for labels, mode, reason in _DEFAULT_EMOTION_TO_MODE:
            if emotion_label in labels:
                if mode == "安慰" and emotion_intensity >= 1:
                    return ("安慰", reason, None, None)
                if mode == "闲聊":
                    return ("闲聊", reason, None, None)
                if mode == "倾听":
                    return ("倾听", reason, None, None)

    return ("倾听", "默认倾听", None, None)


def get_system_prompt_for_mode(mode: Mode) -> str:
    """返回指定 mode 对应的 system prompt 模板（优先使用已加载的配置文件）。"""
    if _policy_config:
        prompts = _policy_config.get("mode_prompts") or {}
        if isinstance(prompts, dict) and mode in prompts:
            return prompts[mode]
    return _DEFAULT_MODE_PROMPTS.get(mode) or _DEFAULT_MODE_PROMPTS["倾听"]
