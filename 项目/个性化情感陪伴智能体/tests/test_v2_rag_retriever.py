"""
V2 第一功能：最小向量检索层（app/rag）基础测试。
"""

from __future__ import annotations

from app.memory.ltm import LTMItem
from app.rag import LTMRetriever


def _item(*, id: str, user_id: str, content: str, type: str = "Preference") -> LTMItem:
    return LTMItem(
        id=id,
        user_id=user_id,
        type=type,  # type: ignore[arg-type]
        content=content,
        created_at=1,
        source="test",
        confidence=1.0,
        tags=[],
    )


def test_retrieve_prefers_similar_memory():
    """相似 query 命中同语义记忆，score 倒序。"""
    r = LTMRetriever()
    r.index_item(_item(id="a", user_id="u1", content="不喜欢鸡汤，回答直接一点"))
    r.index_item(_item(id="b", user_id="u1", content="周末喜欢打羽毛球"))
    r.index_item(_item(id="c", user_id="u1", content="叫我小张"))

    hits = r.retrieve(user_id="u1", query="不要鸡汤", top_k=2)
    assert len(hits) >= 1
    assert hits[0].item.id == "a"
    if len(hits) > 1:
        assert hits[0].score >= hits[1].score


def test_retrieve_is_user_isolated():
    """不同 user 的记忆互不召回。"""
    r = LTMRetriever()
    r.index_item(_item(id="u1a", user_id="u1", content="叫我小张"))
    r.index_item(_item(id="u2a", user_id="u2", content="叫我老李"))

    hits_u1 = r.retrieve(user_id="u1", query="叫我")
    ids_u1 = {x.item.id for x in hits_u1}
    assert "u1a" in ids_u1
    assert "u2a" not in ids_u1

