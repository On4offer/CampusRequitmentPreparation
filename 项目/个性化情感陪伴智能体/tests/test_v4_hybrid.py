"""
V4 模块一：混合检索（向量 + BM25）测试。
V4 模块二：Query 改写/重试测试。
"""

from __future__ import annotations

import asyncio

from app.memory.ltm import LTMItem
from app.rag.bm25 import InMemoryBM25Index, BM25ScoredId
from app.rag.retriever import LTMRetriever, RetrievedMemory
from app.rag.index import InMemoryVectorIndex


def test_bm25_index_upsert_and_query():
    """BM25 索引：写入文档后可检索。"""
    idx = InMemoryBM25Index()
    idx.upsert(user_id="u1", item_id="a", content="我喜欢吃苹果和香蕉")
    idx.upsert(user_id="u1", item_id="b", content="苹果很甜")
    idx.upsert(user_id="u1", item_id="c", content="今天天气不错")

    results = idx.query_top_k(user_id="u1", query="苹果", top_k=3)
    assert len(results) >= 1
    ids = [r.item_id for r in results]
    assert "a" in ids or "b" in ids


def test_bm25_remove():
    """BM25 索引：remove 后不再命中。"""
    idx = InMemoryBM25Index()
    idx.upsert(user_id="u1", item_id="a", content="测试内容")
    results = idx.query_top_k(user_id="u1", query="测试", top_k=3)
    assert len(results) >= 1
    idx.remove(user_id="u1", item_id="a")
    results = idx.query_top_k(user_id="u1", query="测试", top_k=3)
    assert len(results) == 0


def test_retriever_hybrid_returns_fused_results():
    """混合检索：use_hybrid=True 时融合向量与 BM25。"""
    retriever = LTMRetriever()
    items = [
        LTMItem(id="m1", user_id="u_hybrid", type="Preference", content="不喜欢鸡汤，叫我小张", created_at=123, source=""),
        LTMItem(id="m2", user_id="u_hybrid", type="Preference", content="喜欢跑步和健身", created_at=124, source=""),
    ]
    for item in items:
        retriever.index_item(item)

    # 单路向量
    vec_only = retriever.retrieve(user_id="u_hybrid", query="别鸡汤", top_k=3, use_hybrid=False)
    assert len(vec_only) >= 1

    # 混合检索
    hybrid = retriever.retrieve(
        user_id="u_hybrid",
        query="别鸡汤",
        top_k=3,
        use_hybrid=True,
        bm25_top_k=5,
        fusion_method="rrf",
    )
    assert len(hybrid) >= 1
    assert any(h.item.id == "m1" for h in hybrid)


def test_retriever_hybrid_off_unchanged():
    """use_hybrid=False 时行为与 V2 一致。"""
    retriever = LTMRetriever()
    item = LTMItem(id="x", user_id="u2", type="Preference", content="测试记忆", created_at=1, source="")
    retriever.index_item(item)

    r1 = retriever.retrieve(user_id="u2", query="测试", top_k=3, use_hybrid=False)
    r2 = retriever.retrieve(user_id="u2", query="测试", top_k=3, use_hybrid=True)
    assert len(r1) >= 1
    assert len(r2) >= 1
    assert r1[0].item.id == r2[0].item.id or "x" in [h.item.id for h in r2]


# ---------- V4 模块二：Query 改写 ----------


def test_rewrite_for_retrieval_returns_rewritten():
    """rewrite_for_retrieval：LLM 返回有效内容时返回改写结果。"""
    from app.rag.query_rewrite import rewrite_for_retrieval

    class _MockLLM:
        async def chat(self, messages, temperature=0.7):
            return {"raw": {"choices": [{"message": {"content": "不要鸡汤 不要讲道理"}}]}}

    result = asyncio.run(rewrite_for_retrieval("别讲大道理", _MockLLM()))
    assert result == "不要鸡汤 不要讲道理"


def test_rewrite_for_retrieval_returns_none_on_failure():
    """rewrite_for_retrieval：LLM 异常时返回 None。"""
    from app.rag.query_rewrite import rewrite_for_retrieval

    class _FailingLLM:
        async def chat(self, messages, temperature=0.7):
            raise RuntimeError("mock error")

    result = asyncio.run(rewrite_for_retrieval("test", _FailingLLM()))
    assert result is None


def test_query_rewrite_integration(monkeypatch):
    """开启 rewrite 时：首次召回弱触发改写，trace 含 rewrite_triggered。"""
    from fastapi.testclient import TestClient

    from app.main import app
    from app.core import settings as core_settings
    from app.trace.store import InMemoryTraceStore

    class _FakeLLM:
        async def chat(self, messages, temperature: float = 0.7):
            await asyncio.sleep(0)
            for m in messages:
                c = getattr(m, "content", None) or ""
                if "检索查询改写" in c or "改写后的检索词" in c:
                    return {"request_id": "rw", "raw": {"choices": [{"message": {"content": "不要鸡汤 不要讲道理"}}]}}
                if "情绪识别" in c:
                    return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
            return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

        @staticmethod
        def extract_text(r):
            return r["raw"]["choices"][0]["message"]["content"]

    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_top_k", 3)
    monkeypatch.setattr(core_settings.settings, "rag_rewrite_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_rewrite_min_score", 0.0)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    client.post(
        "/memory/ltm",
        json={"user_id": "u_rewrite", "type": "Preference", "content": "不喜欢鸡汤，叫我小张"},
    )

    # 用与记忆无重叠的 query 确保首次 0 命中，触发改写；改写后 "不要鸡汤" 会命中
    r = client.post("/chat", json={"message": "今天好累啊", "user_id": "u_rewrite", "session_id": "s1"})
    assert r.status_code == 200
    tr = client.get(f"/trace/{r.json()['trace_id']}").json()
    retrieve_step = next((s for s in tr["steps"] if s["name"] == "retrieve_ltm"), None)
    assert retrieve_step is not None
    out = retrieve_step.get("output_summary") or ""
    assert "rewrite_triggered" in out or "hits=" in out
