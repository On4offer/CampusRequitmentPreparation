"""
V5 内容安全：规则层输入扫描与输出替换（可后续接 LLM 审核）。

- 与情绪模块中的「自伤/高风险」关键词互补：此处侧重违法、极端暴力等可运营扩展词表。
- trace 只写类别标签，避免把用户原文写入 decision。
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InputContentScan:
    """用户输入扫描结果。"""

    force_safety: bool = False
    """为 True 时应与安全模式一致处理（使用 SAFE_SYSTEM_PROMPT 等）。"""
    matched_categories: list[str] = field(default_factory=list)
    """命中规则类别，用于审计（如 illegal_drug、extreme_violence）。"""


# (关键词, 类别)；命中任一即 force_safety。类别用于 trace，不写具体词。
_FORCE_SAFETY_KEYWORDS: tuple[tuple[str, str], ...] = (
    ("制毒", "illegal_drug"),
    ("贩毒", "illegal_drug"),
    ("贩卖毒品", "illegal_drug"),
    ("买凶", "extreme_violence"),
    ("雇凶", "extreme_violence"),
    ("砍死", "extreme_violence"),
    ("弄死他", "extreme_violence"),
    ("弄死她", "extreme_violence"),
    ("炸弹制作", "extreme_violence"),
    ("恐怖袭击", "extreme_violence"),
    ("儿童色情", "csam"),
    ("猥亵儿童", "csam"),
    ("强奸未成年人", "sexual_violence"),
)


# 输出脱敏：在输入词表基础上增加易出现在模型复述中的词（输入侧不扫「毒品」以免误伤科普语境）
_OUTPUT_ONLY: tuple[tuple[str, str], ...] = (("毒品", "illegal_drug"),)

# 按长度降序优先替换长词
_OUTPUT_BLOCKLIST: tuple[tuple[str, str], ...] = tuple(
    sorted(_FORCE_SAFETY_KEYWORDS + _OUTPUT_ONLY, key=lambda x: len(x[0]), reverse=True)
)


def scan_user_input(text: str | None) -> InputContentScan:
    """扫描用户输入；命中强制安全词表则 force_safety=True。"""
    if not text or not str(text).strip():
        return InputContentScan(False, [])
    t = str(text)
    cats: list[str] = []
    for kw, cat in _FORCE_SAFETY_KEYWORDS:
        if kw in t:
            cats.append(cat)
    if not cats:
        return InputContentScan(False, [])
    # 去重保序
    seen: set[str] = set()
    uniq = []
    for c in cats:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return InputContentScan(True, uniq)


def sanitize_assistant_output(text: str) -> tuple[str, list[str]]:
    """
    对助手输出做规则脱敏；返回 (脱敏后文本, 命中类别列表)。
    """
    if not text:
        return text, []
    out = str(text)
    tags: list[str] = []
    for kw, cat in _OUTPUT_BLOCKLIST:
        if kw in out:
            out = out.replace(kw, "***")
            tags.append(cat)
    if not tags:
        return out, []
    seen: set[str] = set()
    uniq = []
    for c in tags:
        if c not in seen:
            seen.add(c)
            uniq.append(c)
    return out, uniq


def merge_safety_trace_reason(
    *,
    safety_mode: bool,
    safety_trigger_reason: str | None,
    output_filter_tags: list[str] | None,
) -> tuple[bool, str | None]:
    """
    生成 TraceDecision.safety_triggered / safety_reason（可审计、简短）。

    safety_trigger_reason：已由路由合并情绪与输入内容安全原因。
    """
    outs = output_filter_tags or []
    triggered = bool(safety_mode or outs)
    parts: list[str] = []
    if safety_mode:
        parts.append(safety_trigger_reason or "safety_mode")
    if outs:
        parts.append("输出脱敏:" + ",".join(outs))
    reason = "; ".join(parts) if triggered else None
    return triggered, reason
