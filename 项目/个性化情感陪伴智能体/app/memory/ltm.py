"""
长期记忆（LTM）数据模型与占位存储（V1）。

类型：Preference / Profile / Event / Constraint。
最小字段：id, user_id, type, content, created_at, source, confidence, tags（可选）。
占位实现为内存存储；V2 可替换为向量库/DB 并在此接口上做检索。
"""

from __future__ import annotations

import threading
import uuid
from typing import Literal

from pydantic import BaseModel, Field

LTMType = Literal["Preference", "Profile", "Event", "Constraint"]


class LTMItem(BaseModel):
    """单条长期记忆条目。"""

    id: str = Field(default="", description="唯一标识，写入时为空则自动生成")
    user_id: str = Field(..., description="所属用户")
    type: LTMType = Field(..., description="Preference/Profile/Event/Constraint")
    content: str = Field(..., min_length=1, description="记忆内容")
    created_at: int = Field(..., description="创建时间戳（毫秒）")
    source: str = Field(default="", description="来源（如 dialogue/admin）")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="置信度 0~1")
    tags: list[str] = Field(default_factory=list, description="可选标签")
    is_active: bool = Field(default=True, description="是否生效（软删除用）")
    updated_at: int = Field(default=0, description="更新时间戳（毫秒）")
    embedding_status: Literal["pending", "ready", "failed"] = Field(default="pending", description="向量状态")


class InMemoryLTMStore:
    """LTM 占位存储：内存 dict，按 user_id + type 过滤列表。"""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._by_id: dict[str, LTMItem] = {}
        self._by_user: dict[str, list[str]] = {}  # user_id -> [id, ...] 按写入顺序

    def put(self, user_id: str, item: LTMItem) -> str:
        """写入或覆盖一条；若 item.id 为空则生成新 id。返回最终 id。"""
        now = item.created_at
        if item.updated_at <= 0:
            item = item.model_copy(update={"updated_at": now})
        uid = (item.id or "").strip()
        if not uid:
            uid = str(uuid.uuid4())
            item = item.model_copy(update={"id": uid, "user_id": user_id})
        else:
            item = item.model_copy(update={"user_id": user_id})
        with self._lock:
            self._by_id[uid] = item
            if user_id not in self._by_user:
                self._by_user[user_id] = []
            if uid not in self._by_user[user_id]:
                self._by_user[user_id].append(uid)
        return uid

    def update_item(
        self,
        *,
        id: str,
        content: str | None = None,
        tags: list[str] | None = None,
        confidence: float | None = None,
        is_active: bool | None = None,
        updated_at: int | None = None,
    ) -> LTMItem | None:
        """按 id 局部更新一条记忆。"""
        with self._lock:
            cur = self._by_id.get(id)
            if cur is None:
                return None
            update: dict = {}
            if content is not None:
                update["content"] = content
            if tags is not None:
                update["tags"] = tags
            if confidence is not None:
                update["confidence"] = confidence
            if is_active is not None:
                update["is_active"] = is_active
            update["updated_at"] = int(updated_at or cur.updated_at or cur.created_at)
            nxt = cur.model_copy(update=update)
            self._by_id[id] = nxt
            return nxt

    def soft_delete(self, *, id: str, updated_at: int | None = None) -> LTMItem | None:
        """软删除：标记 is_active=false。"""
        return self.update_item(id=id, is_active=False, updated_at=updated_at)

    def get_by_id(self, id: str) -> LTMItem | None:
        """按 id 查询。"""
        with self._lock:
            return self._by_id.get(id)

    def list_by_user(
        self,
        user_id: str,
        type: LTMType | None = None,
        limit: int = 20,
        q: str | None = None,
        only_active: bool = True,
    ) -> list[LTMItem]:
        """按 user_id 列表，可选 type 过滤；按写入顺序倒序，最多 limit 条。"""
        q_norm = (q or "").strip().lower()
        with self._lock:
            ids = self._by_user.get(user_id, [])[::-1]
            out: list[LTMItem] = []
            for i in ids:
                if len(out) >= limit:
                    break
                item = self._by_id.get(i)
                if item is None:
                    continue
                if only_active and not item.is_active:
                    continue
                if type is not None and item.type != type:
                    continue
                if q_norm and q_norm not in item.content.lower():
                    continue
                out.append(item)
            return out


ltm_store = InMemoryLTMStore()
