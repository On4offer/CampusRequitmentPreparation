"""
V4 混合检索：BM25 索引（内存版）。

与 embedder 共用 tokenize，按 user_id 分桶，支持 upsert/remove/query。
"""

from __future__ import annotations

import math
import threading
from collections import Counter
from dataclasses import dataclass

from app.rag.embedder import tokenize


@dataclass(frozen=True)
class BM25ScoredId:
    item_id: str
    score: float


class InMemoryBM25Index:
    """
    内存 BM25 索引：按 user_id 分桶存储文档。
    文档为 LTM content，分词后计算 BM25 得分。
    """

    def __init__(self, *, k1: float = 1.2, b: float = 0.75) -> None:
        self._k1 = k1
        self._b = b
        self._lock = threading.Lock()
        # user_id -> item_id -> list of tokens
        self._docs: dict[str, dict[str, list[str]]] = {}
        # user_id -> (doc_count, avgdl, term_doc_freq)
        self._stats: dict[str, tuple[int, float, dict[str, int]]] = {}

    def upsert(self, *, user_id: str, item_id: str, content: str) -> None:
        """写入或更新文档。"""
        if not user_id or not item_id or not (content or "").strip():
            return
        tokens = tokenize(content)
        if not tokens:
            return
        with self._lock:
            self._docs.setdefault(user_id, {})[item_id] = tokens
            self._recompute_stats(user_id)

    def remove(self, *, user_id: str, item_id: str) -> None:
        """移除文档。"""
        with self._lock:
            bucket = self._docs.get(user_id)
            if not bucket:
                return
            bucket.pop(item_id, None)
            if bucket:
                self._recompute_stats(user_id)
            else:
                self._stats.pop(user_id, None)

    def _recompute_stats(self, user_id: str) -> None:
        """重新计算该 user 的 N、avgdl、term_doc_freq。"""
        bucket = self._docs.get(user_id, {})
        if not bucket:
            self._stats.pop(user_id, None)
            return
        N = len(bucket)
        total_len = 0
        term_doc_freq: dict[str, int] = {}
        for item_id, tokens in bucket.items():
            doc_len = len(tokens)
            total_len += doc_len
            for t in set(tokens):
                term_doc_freq[t] = term_doc_freq.get(t, 0) + 1
        avgdl = total_len / N if N > 0 else 0.0
        self._stats[user_id] = (N, avgdl, term_doc_freq)

    def query_top_k(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int,
    ) -> list[BM25ScoredId]:
        """
        BM25 检索，返回 top_k 结果。
        """
        if top_k <= 0:
            return []
        tokens = tokenize(query)
        if not tokens:
            return []

        with self._lock:
            bucket = self._docs.get(user_id, {})
            stats = self._stats.get(user_id)
            if not bucket or not stats:
                return []
            N, avgdl, term_doc_freq = stats
            if N <= 0 or avgdl <= 0:
                return []

            scores: list[BM25ScoredId] = []
            for item_id, doc_tokens in bucket.items():
                doc_len = len(doc_tokens)
                tf = Counter(doc_tokens)
                score = 0.0
                for t in set(tokens):
                    if t not in tf:
                        continue
                    n_t = term_doc_freq.get(t, 0)
                    idf = math.log((N - n_t + 0.5) / (n_t + 0.5) + 1.0)
                    f_td = tf[t]
                    score += idf * (f_td * (self._k1 + 1)) / (
                        f_td + self._k1 * (1 - self._b + self._b * doc_len / avgdl)
                    )
                if score > 0:
                    scores.append(BM25ScoredId(item_id=item_id, score=score))

            scores.sort(key=lambda x: x.score, reverse=True)
            return scores[:top_k]
