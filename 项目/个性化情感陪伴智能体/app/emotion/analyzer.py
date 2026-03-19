"""
情绪识别：LLM 为主、关键词兜底。

- 风险分层：仍用关键词（保证高危不漏、可解释）。
- 情绪 label/intensity/evidence：优先调用 LLM；失败或解析异常时回退到规则。
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Literal

from app.llm.client import ChatMessage, LLMClient

RiskTier = Literal["一般", "关注", "高风险"]
EmotionLabel = Literal["开心", "平静", "低落", "焦虑", "愤怒", "疲惫"]

VALID_LABELS: frozenset[str] = frozenset({"开心", "平静", "低落", "焦虑", "愤怒", "疲惫"})


@dataclass
class EmotionResult:
    """单次情绪分析结果。"""

    label: EmotionLabel | str
    intensity: int  # 0-3
    evidence: str
    risk_tier: RiskTier


# ---------- 风险分层：始终用关键词（安全优先、可解释） ----------

_HIGH_RISK_KEYWORDS = (
    "自杀", "想死", "不想活", "自残", "自伤", "跳楼", "上吊", "割腕",
    "杀人", "伤害别人", "同归于尽", "活不下去", "了结",
)
_WATCH_KEYWORDS = (
    "抑郁", "崩溃", "撑不住", "没人懂", "想消失", "没意思",
)


def _risk_from_keywords(text: str) -> tuple[RiskTier, str]:
    """仅做风险分层，返回 (risk_tier, evidence)。"""
    t = text.strip() if text else ""
    for kw in _HIGH_RISK_KEYWORDS:
        if kw in t:
            return ("高风险", kw)
    for kw in _WATCH_KEYWORDS:
        if kw in t:
            return ("关注", kw)
    return ("一般", "")


# ---------- 规则兜底：LLM 失败时用 ----------

_EMOTION_RULES: list[tuple[tuple[str, ...], EmotionLabel, int]] = [
    (("开心", "高兴", "哈哈", "嘿嘿", "棒", "太好了"), "开心", 2),
    (("焦虑", "紧张", "担心", "慌", "烦躁"), "焦虑", 2),
    (("愤怒", "生气", "气死", "烦死了", "火大"), "愤怒", 2),
    (("低落", "难过", "伤心", "郁闷", "委屈"), "低落", 2),
    (("累", "疲惫", "困", "没劲"), "疲惫", 2),
    (("平静", "还好", "一般", "没事"), "平静", 1),
]


def _emotion_from_rules(text: str) -> tuple[EmotionLabel | str, int, str]:
    """规则匹配情绪，返回 (label, intensity, evidence)。"""
    t = (text or "").strip()
    if not t:
        return ("平静", 0, "(空输入)")
    for keywords, label, intensity in _EMOTION_RULES:
        for kw in keywords:
            if kw in t:
                return (label, intensity, kw)
    return ("平静", 0, "默认平静")


# ---------- LLM 情绪解析 ----------

_EMOTION_SYSTEM_PROMPT = """你是一个情绪识别助手。根据用户输入，只输出一个 JSON，不要其他文字。
格式：{"label":"开心|平静|低落|焦虑|愤怒|疲惫","intensity":0到3的整数,"evidence":"用户原话中体现该情绪的短句或关键词"}
label 必须从上述六选一；intensity 0最弱、3最强；evidence 尽量用用户原话中的短语。"""


def _parse_emotion_json(raw: str) -> tuple[EmotionLabel | str, int, str] | None:
    """从 LLM 回复中解析 JSON，返回 (label, intensity, evidence) 或 None。"""
    raw = (raw or "").strip()
    # 允许被 ```json ... ``` 包裹
    m = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
    if not m:
        return None
    try:
        obj = json.loads(m.group())
        label = (obj.get("label") or "").strip()
        if label not in VALID_LABELS:
            return None
        intensity = obj.get("intensity")
        if intensity is None:
            intensity = 0
        else:
            try:
                intensity = int(intensity)
            except (TypeError, ValueError):
                intensity = 0
        intensity = max(0, min(3, intensity))
        evidence = (obj.get("evidence") or "").strip() or label
        return (label, intensity, evidence)
    except (json.JSONDecodeError, TypeError):
        return None


async def analyze_emotion(text: str, *, llm: LLMClient) -> EmotionResult:
    """
    情绪识别：风险用关键词，情绪优先 LLM、失败则规则兜底。

    - risk_tier / 高风险证据：始终来自关键词。
    - label / intensity / evidence：先调 LLM 单轮；解析失败或请求异常时用规则结果。
    """
    if not (text or "").strip():
        risk_tier, evidence_risk = _risk_from_keywords("")
        return EmotionResult(label="平静", intensity=0, evidence="(空输入)", risk_tier=risk_tier)

    risk_tier, evidence_risk = _risk_from_keywords(text)
    label: EmotionLabel | str = "平静"
    intensity = 0
    evidence_emotion = ""

    try:
        messages = [
            ChatMessage(role="system", content=_EMOTION_SYSTEM_PROMPT),
            ChatMessage(role="user", content=text),
        ]
        resp = await llm.chat(messages, temperature=0.1)
        content = llm.extract_text(resp).strip()
        parsed = _parse_emotion_json(content)
        if parsed:
            label, intensity, evidence_emotion = parsed
    except Exception:
        pass

    if not evidence_emotion:
        label, intensity, evidence_emotion = _emotion_from_rules(text)

    if risk_tier == "高风险":
        evidence = evidence_risk or "高风险关键词"
    elif evidence_emotion:
        evidence = evidence_emotion
        if evidence_risk:
            evidence = f"{evidence_emotion};{evidence_risk}"
    else:
        evidence = evidence_risk or evidence_emotion or "默认平静"

    return EmotionResult(
        label=label,
        intensity=intensity,
        evidence=evidence,
        risk_tier=risk_tier,
    )
