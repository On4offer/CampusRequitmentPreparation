"""LangChain Retriever / LCEL RAG 与进程内 `ltm_retriever.retrieve` 结果对齐（无真实 LLM）。"""

from __future__ import annotations

import pytest

from app.langchain.ltm_retriever_lc import LTMRetrieverLC
from app.langchain.rag_lcel import make_ltm_rag_runnable
from app.memory.ltm import LTMItem
from app.rag import ltm_retriever


@pytest.fixture
def indexed_memory():
    """向单例索引写入一条记忆，便于检索。"""
    uid = "u_lc_test"
    item = LTMItem(
        id="mem_lc_1",
        user_id=uid,
        type="Preference",
        content="用户喜欢喝燕麦拿铁",
        created_at=1_700_000_000_000,
        source="test",
    )
    ltm_retriever.index_item(item)
    yield uid, item
    try:
        ltm_retriever.remove_item(item)
    except Exception:
        pass


def test_ltm_retriever_lc_matches_direct_retrieve(indexed_memory):
    uid, item = indexed_memory
    q = "咖啡口味"
    direct = ltm_retriever.retrieve(user_id=uid, query=q, top_k=3, min_score=0.0)
    r = LTMRetrieverLC(user_id=uid, top_k=3, min_score=0.0)
    docs = r.invoke(q)
    assert len(docs) == len(direct)
    if direct:
        assert docs[0].metadata.get("id") == direct[0].item.id
        assert "Preference" in docs[0].page_content


def test_make_ltm_rag_runnable_pack_and_budget(indexed_memory):
    uid, _item = indexed_memory
    chain = make_ltm_rag_runnable(user_id=uid, max_chars=500)
    out = chain.invoke("拿铁")
    assert out.get("raw_n_docs", 0) >= 1
    assert "燕麦" in (out.get("evidence_body") or "")
    assert out.get("memory_hits")
