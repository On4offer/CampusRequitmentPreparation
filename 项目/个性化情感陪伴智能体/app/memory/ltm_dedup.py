"""
V1.1 P1：隐式 LTM 写入前的规则去重（与已有条目比相似度）。

- sim >= skip_ratio：视为重复，不新建不更新。
- merge_ratio <= sim < skip_ratio：合并更新已有条目（内容/标签/置信度取优）并依赖上层重索引。
"""

from __future__ import annotations

import re
from difflib import SequenceMatcher

from app.memory.ltm import LTMItem, LTMType


def norm_for_dedup(text: str) -> str:
    s = (text or "").strip().lower()
    s = re.sub(r"[\s\u3000]+", "", s)
    s = re.sub(r"[^\w\u4e00-\u9fff]", "", s)
    return s


def content_similarity(a: str, b: str) -> float:
    na, nb = norm_for_dedup(a), norm_for_dedup(b)
    if not na and not nb:
        return 1.0
    if not na or not nb:
        return 0.0
    return float(SequenceMatcher(None, na, nb).ratio())


def best_match_same_type(
    *,
    content: str,
    typ: LTMType,
    candidates: list[LTMItem],
) -> tuple[LTMItem | None, float]:
    best: LTMItem | None = None
    best_r = 0.0
    for row in candidates:
        if row.type != typ or not row.is_active:
            continue
        r = content_similarity(content, row.content)
        if r > best_r:
            best_r = r
            best = row
    return best, best_r
