from __future__ import annotations

"""
V2 最小 embedding：把文本映射为稀疏向量（token -> weight）。

说明：
- 仅用于本地最小 RAG 验证，不依赖外部 embedding 服务。
- 规则简单、可解释、无额外依赖；后续可替换成真实 embedding 模型。
"""

import math
import re
from collections import Counter


_ASCII_TOKEN_RE = re.compile(r"[A-Za-z0-9_]+")


def _tokenize(text: str) -> list[str]:
    """
    粗粒度分词：
    - 英文/数字：按连续 token 切分并小写
    - 中文：按单字切分（去空白）
    """
    t = (text or "").strip()
    if not t:
        return []

    ascii_tokens = [x.lower() for x in _ASCII_TOKEN_RE.findall(t)]
    # 去掉 ASCII token 后，再把剩余非空白字符按单字加入（覆盖中文场景）
    rest = _ASCII_TOKEN_RE.sub(" ", t)
    zh_chars = [ch for ch in rest if not ch.isspace()]
    return [*ascii_tokens, *zh_chars]


def embed_text(text: str) -> dict[str, float]:
    """
    生成 L2 归一化稀疏向量。
    返回：{token: normalized_tf}
    """
    tokens = _tokenize(text)
    if not tokens:
        return {}

    tf = Counter(tokens)
    norm = math.sqrt(sum(v * v for v in tf.values()))
    if norm <= 0:
        return {}
    return {k: (v / norm) for k, v in tf.items()}

