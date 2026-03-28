"""RAG 进程内索引与 MySQL LTM 的同步：启动时把已持久化的活跃 LTM 灌回 `ltm_retriever`。"""

from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


def warm_ltm_retriever_from_store() -> int:
    """
    在 RAG_ENABLED=true 时，从 `ltm_store` 拉取 is_active 条目并 index_item。

    解决：LTM 在 MySQL、向量/BM25 索引仅在内存；进程重启后若不预热则 /chat 检索不到库中旧数据。
    """
    from app.core.settings import settings

    if not getattr(settings, "rag_enabled", False):
        return 0

    from app.memory.ltm import ltm_store
    from app.rag import ltm_retriever

    if not hasattr(ltm_store, "iter_active_ltm_items"):
        return 0

    n = 0
    for item in ltm_store.iter_active_ltm_items():
        try:
            ltm_retriever.index_item(item)
            n += 1
        except Exception as e:
            logger.warning("RAG 预热跳过 id=%s: %s", getattr(item, "id", "?"), e)
    return n
