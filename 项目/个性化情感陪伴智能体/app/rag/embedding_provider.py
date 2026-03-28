"""
RAG 向量：默认稀疏本地 embed；可选 OpenAI 兼容 /embeddings，失败时回退稀疏并打日志。

V1.1 P2：与外部向量服务对齐的最小接入（维度索引映射为稀疏 dict，沿用现有点积检索）。
"""

from __future__ import annotations

import logging
import math
from typing import Any

from app.core.settings import settings
from app.rag.embedder import embed_text as sparse_embed_text

logger = logging.getLogger(__name__)


def _l2_normalize_dense(vec: list[float]) -> dict[str, float]:
    if not vec:
        return {}
    s = math.sqrt(sum(v * v for v in vec))
    if s <= 0:
        return {}
    return {str(i): float(v) / s for i, v in enumerate(vec)}


def embed_for_rag(text: str) -> dict[str, float]:
    """
    返回与 InMemoryVectorIndex 兼容的稀疏向量（已 L2 归一化，点积≈余弦）。
    """
    base = (getattr(settings, "rag_embedding_api_base", "") or "").strip()
    if not base:
        return sparse_embed_text(text)

    import httpx

    key = (getattr(settings, "rag_embedding_api_key", "") or "").strip()
    model = (getattr(settings, "rag_embedding_model", "") or "").strip() or "text-embedding-3-small"
    url = base.rstrip("/") + "/embeddings"
    headers: dict[str, str] = {"Content-Type": "application/json"}
    if key:
        headers["Authorization"] = f"Bearer {key}"
    payload: dict[str, Any] = {"model": model, "input": (text or "")[:8000]}

    try:
        with httpx.Client(timeout=float(getattr(settings, "rag_embedding_timeout_s", 30.0) or 30.0)) as client:
            r = client.post(url, json=payload, headers=headers)
            r.raise_for_status()
            data = r.json()
        emb = (data.get("data") or [{}])[0].get("embedding")
        if not isinstance(emb, list):
            raise ValueError("embedding missing")
        vec = [float(x) for x in emb]
        out = _l2_normalize_dense(vec)
        if out:
            return out
    except Exception as e:
        logger.warning("rag remote embedding failed, fallback sparse: %s", e)

    return sparse_embed_text(text)
