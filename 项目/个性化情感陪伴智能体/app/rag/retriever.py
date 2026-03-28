from __future__ import annotations

"""
V2 最小 retriever：把 LTMItem 写入向量索引，并按 query 检索。
V4 扩展：混合检索（向量 + BM25），RRF 融合。
"""

from dataclasses import dataclass
from app.memory.ltm import LTMItem
from app.rag.embedding_provider import embed_for_rag
from app.rag.index import InMemoryVectorIndex, ScoredId
from app.rag.bm25 import InMemoryBM25Index, BM25ScoredId


@dataclass(frozen=True)
class RetrievedMemory:
    item: LTMItem
    score: float


def _rrf_fusion(
    vector_results: list[ScoredId],
    bm25_results: list[BM25ScoredId],
    *,
    k: int = 60,
) -> list[tuple[str, float]]:
    """
    RRF（Reciprocal Rank Fusion）融合两路检索结果。
    返回 [(item_id, rrf_score), ...] 按 score 降序。
    """
    rrf_scores: dict[str, float] = {}
    for rank, x in enumerate(vector_results, start=1):
        rrf_scores[x.item_id] = rrf_scores.get(x.item_id, 0.0) + 1.0 / (k + rank)
    for rank, x in enumerate(bm25_results, start=1):
        rrf_scores[x.item_id] = rrf_scores.get(x.item_id, 0.0) + 1.0 / (k + rank)
    sorted_ids = sorted(rrf_scores.items(), key=lambda p: p[1], reverse=True)
    return sorted_ids


class LTMRetriever:
    """LTM 检索器（内存索引版）。V4 支持混合检索（向量 + BM25）。"""

    def __init__(
        self,
        *,
        index: InMemoryVectorIndex | None = None,
        bm25_index: InMemoryBM25Index | None = None,
    ) -> None:
        self.index = index or InMemoryVectorIndex()
        self.bm25_index = bm25_index or InMemoryBM25Index()
        self._items_by_id: dict[str, LTMItem] = {}

    def index_item(self, item: LTMItem) -> None:
        vec = embed_for_rag(item.content)
        self._items_by_id[item.id] = item
        self.index.upsert(user_id=item.user_id, item_id=item.id, vector=vec)
        self.bm25_index.upsert(user_id=item.user_id, item_id=item.id, content=item.content)

    def remove_item(self, item: LTMItem) -> None:
        self._items_by_id.pop(item.id, None)
        self.index.remove(user_id=item.user_id, item_id=item.id)
        self.bm25_index.remove(user_id=item.user_id, item_id=item.id)

    def retrieve(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0,
        use_hybrid: bool = False,
        bm25_top_k: int = 5,
        fusion_method: str = "rrf",
    ) -> list[RetrievedMemory]:
        """
        检索 LTM。use_hybrid=True 时融合向量与 BM25；
        fusion_method 支持 rrf（默认）或 weighted。
        """
        if use_hybrid:
            return self._retrieve_hybrid(
                user_id=user_id,
                query=query,
                top_k=top_k,
                min_score=min_score,
                bm25_top_k=bm25_top_k,
                fusion_method=fusion_method,
            )
        return self._retrieve_vector_only(
            user_id=user_id,
            query=query,
            top_k=top_k,
            min_score=min_score,
        )

    def _retrieve_vector_only(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int,
        min_score: float,
    ) -> list[RetrievedMemory]:
        """单路向量检索（V2 行为）。"""
        qv = embed_for_rag(query)
        scored = self.index.query_top_k(
            user_id=user_id,
            query_vector=qv,
            top_k=top_k,
            min_score=min_score,
        )
        out: list[RetrievedMemory] = []
        for x in scored:
            item = self._items_by_id.get(x.item_id)
            if item is None:
                continue
            out.append(RetrievedMemory(item=item, score=x.score))
        return out

    def _retrieve_hybrid(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int,
        min_score: float,
        bm25_top_k: int,
        fusion_method: str,
    ) -> list[RetrievedMemory]:
        """混合检索：向量 + BM25，RRF 或加权融合。"""
        if fusion_method not in ("rrf", "weighted"):
            fusion_method = "rrf"
        qv = embed_for_rag(query)
        vector_results = self.index.query_top_k(
            user_id=user_id,
            query_vector=qv,
            top_k=max(top_k, bm25_top_k),
            min_score=min_score,
        )
        bm25_results = self.bm25_index.query_top_k(
            user_id=user_id,
            query=query,
            top_k=max(top_k, bm25_top_k),
        )

        if fusion_method == "rrf":
            fused = _rrf_fusion(vector_results, bm25_results)
        else:
            # weighted: 简单加权，向量 0.5 + BM25 归一化 0.5
            vec_scores = {x.item_id: x.score for x in vector_results}
            bm25_max = max((x.score for x in bm25_results), default=1.0)
            bm25_scores = {x.item_id: x.score / bm25_max if bm25_max > 0 else 0 for x in bm25_results}
            all_ids = set(vec_scores) | set(bm25_scores)
            fused = [
                (iid, vec_scores.get(iid, 0) * 0.5 + bm25_scores.get(iid, 0) * 0.5)
                for iid in all_ids
            ]
            fused.sort(key=lambda p: p[1], reverse=True)

        out: list[RetrievedMemory] = []
        for item_id, score in fused[:top_k]:
            item = self._items_by_id.get(item_id)
            if item is None:
                continue
            out.append(RetrievedMemory(item=item, score=float(score)))
        return out

