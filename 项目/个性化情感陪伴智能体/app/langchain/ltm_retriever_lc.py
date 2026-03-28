from __future__ import annotations

"""LangChain BaseRetriever 封装：底层仍用全局 ltm_retriever（向量 / 混合检索不变）。"""

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.rag import ltm_retriever


class LTMRetrieverLC(BaseRetriever):
    """按 user_id 与检索参数绑定，query 为自然语言字符串。"""

    user_id: str
    top_k: int = 3
    min_score: float = 0.0
    use_hybrid: bool = False
    bm25_top_k: int = 5
    fusion_method: str = "rrf"

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> list[Document]:
        hits = ltm_retriever.retrieve(
            user_id=self.user_id,
            query=query,
            top_k=self.top_k,
            min_score=self.min_score,
            use_hybrid=self.use_hybrid,
            bm25_top_k=self.bm25_top_k,
            fusion_method=self.fusion_method or "rrf",
        )
        return [
            Document(
                page_content=f"[{h.item.type}] {h.item.content}",
                metadata={"id": h.item.id, "type": h.item.type, "score": float(h.score)},
            )
            for h in hits
        ]
