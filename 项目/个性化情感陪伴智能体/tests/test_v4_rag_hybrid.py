"""
V4 模块一：混合检索（向量 + BM25）测试。

验证：rag_use_hybrid=True 时融合两路检索；关闭时与 V2 单路向量一致。
"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_hybrid_retrieval_returns_hits(monkeypatch):
    """开启 rag_use_hybrid 时，先写入 LTM，再 /chat，应返回 citations。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_use_hybrid", True)
    monkeypatch.setattr(core_settings.settings, "rag_bm25_top_k", 5)
    monkeypatch.setattr(core_settings.settings, "rag_fusion_method", "rrf")
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r0 = client.post(
        "/memory/ltm",
        json={"user_id": "u_hybrid", "type": "Preference", "content": "不喜欢鸡汤，叫我小张"},
    )
    assert r0.status_code == 200

    r = client.post("/chat", json={"message": "最近有点烦", "user_id": "u_hybrid", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert "citations" in data
    assert len(data["citations"]) >= 1


def test_hybrid_disabled_same_as_vector_only(monkeypatch):
    """rag_use_hybrid=False 时，行为与 V2 单路向量一致。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "rag_enabled", True)
    monkeypatch.setattr(core_settings.settings, "rag_use_hybrid", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r0 = client.post(
        "/memory/ltm",
        json={"user_id": "u_vec", "type": "Preference", "content": "别讲大道理"},
    )
    assert r0.status_code == 200

    r = client.post("/chat", json={"message": "最近有点烦", "user_id": "u_vec", "session_id": "s1"})
    assert r.status_code == 200
    assert len(r.json().get("citations") or []) >= 1


def test_bm25_index_and_rrf_fusion():
    """BM25 索引与 RRF 融合逻辑单元测试。"""
    from app.rag.bm25 import InMemoryBM25Index, BM25ScoredId
    from app.rag.retriever import LTMRetriever, RetrievedMemory
    from app.rag.index import InMemoryVectorIndex, ScoredId
    from app.memory.ltm import LTMItem

    bm25 = InMemoryBM25Index()
    bm25.upsert(user_id="u1", item_id="id1", content="不喜欢鸡汤，叫我小张")
    bm25.upsert(user_id="u1", item_id="id2", content="工作压力大，经常加班")

    results = bm25.query_top_k(user_id="u1", query="鸡汤", top_k=2)
    assert len(results) >= 1
    assert results[0].item_id == "id1"
    assert results[0].score > 0

    # RRF 融合：向量结果 + BM25 结果
    vec_results = [ScoredId("id1", 0.8), ScoredId("id2", 0.3)]
    bm25_results = [BM25ScoredId("id1", 2.5), BM25ScoredId("id3", 1.0)]

    from app.rag.retriever import _rrf_fusion
    fused = _rrf_fusion(vec_results, bm25_results, k=60)
    assert len(fused) >= 2
    # id1 在两路都出现，RRF 分数应最高
    assert fused[0][0] == "id1"
