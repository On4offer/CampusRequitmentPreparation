from __future__ import annotations

"""
V2 最小向量索引（内存版）。

按 user_id 分桶存储 item 向量，支持 upsert / remove / query top-k。
"""

import threading
from dataclasses import dataclass


@dataclass(frozen=True)
class ScoredId:
    item_id: str
    score: float


class InMemoryVectorIndex:
    """简单内存向量索引：user_id -> item_id -> sparse_vector"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_user: dict[str, dict[str, dict[str, float]]] = {}

    def upsert(self, *, user_id: str, item_id: str, vector: dict[str, float]) -> None:
        if not user_id or not item_id:
            return
        with self._lock:
            self._by_user.setdefault(user_id, {})[item_id] = vector

    def remove(self, *, user_id: str, item_id: str) -> None:
        with self._lock:
            bucket = self._by_user.get(user_id)
            if not bucket:
                return
            bucket.pop(item_id, None)

    def query_top_k(
        self,
        *,
        user_id: str,
        query_vector: dict[str, float],
        top_k: int,
        min_score: float = 0.0,
    ) -> list[ScoredId]:
        """
        稀疏向量点积（向量已归一化，等价余弦相似度）。
        """
        if top_k <= 0:
            return []
        if not query_vector:
            return []

        with self._lock:
            bucket = self._by_user.get(user_id, {})
            scores: list[ScoredId] = []
            for item_id, vec in bucket.items():
                score = _dot(query_vector, vec)
                if score >= min_score:
                    scores.append(ScoredId(item_id=item_id, score=score))
            scores.sort(key=lambda x: x.score, reverse=True)
            return scores[:top_k]


def _dot(a: dict[str, float], b: dict[str, float]) -> float:
    if len(a) > len(b):
        a, b = b, a
    s = 0.0
    for k, v in a.items():
        s += v * b.get(k, 0.0)
    return s

