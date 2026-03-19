from __future__ import annotations

"""
V2 最小 retriever：把 LTMItem 写入向量索引，并按 query 检索。
"""

from dataclasses import dataclass

from app.memory.ltm import LTMItem
from app.rag.embedder import embed_text
from app.rag.index import InMemoryVectorIndex


@dataclass(frozen=True)
class RetrievedMemory:
    item: LTMItem
    score: float


class LTMRetriever:
    """LTM 检索器（内存索引版）。"""

    def __init__(self, *, index: InMemoryVectorIndex | None = None) -> None:
        self.index = index or InMemoryVectorIndex()
        self._items_by_id: dict[str, LTMItem] = {}

    def index_item(self, item: LTMItem) -> None:
        vec = embed_text(item.content)
        self._items_by_id[item.id] = item
        self.index.upsert(user_id=item.user_id, item_id=item.id, vector=vec)

    def remove_item(self, item: LTMItem) -> None:
        self._items_by_id.pop(item.id, None)
        self.index.remove(user_id=item.user_id, item_id=item.id)

    def retrieve(
        self,
        *,
        user_id: str,
        query: str,
        top_k: int = 3,
        min_score: float = 0.0,
    ) -> list[RetrievedMemory]:
        qv = embed_text(query)
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

