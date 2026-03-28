from __future__ import annotations

"""
RAG 子链（LCEL）：Retriever → evidence / memory_hits（与进程内混合检索语义一致）。
Query 改写仍为独立异步步，行为对齐 `rag_rewrite_*` 配置。
"""

from typing import Any

from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

from app.core.settings import settings
from app.langchain.ltm_retriever_lc import LTMRetrieverLC
from app.llm.client import LLMClient
from app.rag.query_rewrite import rewrite_for_retrieval


def _pack_docs(docs: list[Document], max_chars: int) -> dict[str, Any]:
    evidence_blocks: list[str] = []
    chars = 0
    memory_hits: list[dict[str, Any]] = []
    for d in docs:
        block = d.page_content
        if chars + len(block) > max_chars:
            break
        evidence_blocks.append(block)
        chars += len(block)
        md = d.metadata or {}
        memory_hits.append(
            {
                "id": md.get("id"),
                "type": md.get("type"),
                "score": round(float(md.get("score", 0.0)), 4),
            }
        )
    return {
        "evidence_body": "\n".join(evidence_blocks),
        "memory_hits": memory_hits if memory_hits else None,
        "raw_n_docs": len(docs),
    }


def make_ltm_rag_runnable(*, user_id: str, max_chars: int) -> Any:
    """LCEL：`LTMRetrieverLC | RunnableLambda(_pack_docs)`，供单测与文档引用。"""
    top_k = int(getattr(settings, "rag_top_k", 3) or 3)
    min_score = float(getattr(settings, "rag_min_score", 0.0) or 0.0)
    use_hybrid = bool(getattr(settings, "rag_use_hybrid", False))
    bm25_top_k = int(getattr(settings, "rag_bm25_top_k", 5) or 5)
    fusion_method = str(getattr(settings, "rag_fusion_method", "rrf") or "rrf")
    retriever = LTMRetrieverLC(
        user_id=user_id,
        top_k=top_k,
        min_score=min_score,
        use_hybrid=use_hybrid,
        bm25_top_k=bm25_top_k,
        fusion_method=fusion_method,
    )
    fmt = RunnableLambda(lambda docs: _pack_docs(docs, max_chars))
    return retriever | fmt


async def build_ltm_rag_via_lcel(
    *,
    user_id: str,
    user_message: str,
    llm: LLMClient | None,
) -> tuple[list | None, list | None, str | None, bool, str | None]:
    """
    返回 (memory_hits, citations, evidence_body, rewrite_triggered, rewritten_query)。
    evidence_body 不含 LTM 块标题（标题由 chat_turn 用 `LTM_RAG_EVIDENCE_HEADER` 拼接）。
    """
    max_chars = int(getattr(settings, "rag_max_chars", 1200) or 1200)
    rewrite_enabled = bool(getattr(settings, "rag_rewrite_enabled", False))
    rewrite_min_score = float(getattr(settings, "rag_rewrite_min_score", 0.0) or 0.0)

    top_k = int(getattr(settings, "rag_top_k", 3) or 3)
    min_score = float(getattr(settings, "rag_min_score", 0.0) or 0.0)
    use_hybrid = bool(getattr(settings, "rag_use_hybrid", False))
    bm25_top_k = int(getattr(settings, "rag_bm25_top_k", 5) or 5)
    fusion_method = str(getattr(settings, "rag_fusion_method", "rrf") or "rrf")
    r = LTMRetrieverLC(
        user_id=user_id,
        top_k=top_k,
        min_score=min_score,
        use_hybrid=use_hybrid,
        bm25_top_k=bm25_top_k,
        fusion_method=fusion_method,
    )

    docs = r.invoke(user_message.strip())
    rewrite_triggered = False
    rewritten_query: str | None = None

    if rewrite_enabled and llm is not None:
        max_score = max((float(d.metadata.get("score", 0.0)) for d in docs), default=0.0)
        if len(docs) == 0 or max_score < rewrite_min_score:
            rw = await rewrite_for_retrieval(user_message, llm, timeout_s=5.0)
            if rw and rw.strip() != user_message.strip():
                docs_retry = r.invoke(rw.strip())
                if len(docs_retry) > len(docs):
                    docs = docs_retry
                    rewrite_triggered = True
                    rewritten_query = rw.strip()

    fmt = RunnableLambda(lambda d: _pack_docs(d, max_chars))
    packed: dict[str, Any] = fmt.invoke(docs)
    body = (packed.get("evidence_body") or "").strip()
    memory_hits = packed.get("memory_hits")
    citations = memory_hits
    evidence_body: str | None = body if body else None
    return memory_hits, citations, evidence_body, rewrite_triggered, rewritten_query
