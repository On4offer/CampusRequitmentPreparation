"""RAG 模块（V2）：最小 embedding/index/retriever。V4：混合检索 BM25。"""

from app.rag.embedder import embed_text, tokenize
from app.rag.index import InMemoryVectorIndex, ScoredId
from app.rag.retriever import LTMRetriever, RetrievedMemory

# 单例：POST /memory/ltm 写入时建索引，/chat 检索时使用
_rag_index = InMemoryVectorIndex()
ltm_retriever = LTMRetriever(index=_rag_index)

__all__ = [
    "embed_text",
    "tokenize",
    "InMemoryVectorIndex",
    "ScoredId",
    "LTMRetriever",
    "RetrievedMemory",
    "ltm_retriever",
]

