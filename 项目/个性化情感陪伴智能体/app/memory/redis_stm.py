"""STM 的 Redis 实现（与 InMemorySessionStore 相同接口）。"""

from __future__ import annotations

import json
import threading
from dataclasses import dataclass
from typing import Any

from app.llm.client import ChatMessage


def _stm_key(user_id: str, session_id: str) -> str:
    """避免 user_id/session_id 中含冒号破坏 key 结构。"""
    u = user_id.replace(":", "_")
    s = session_id.replace(":", "_")
    return f"companion:stm:{u}:{s}"


def _user_index_key(user_id: str) -> str:
    return f"companion:stm:useridx:{user_id.replace(':', '_')}"


@dataclass
class SessionState:
    user_id: str
    session_id: str
    messages: list[ChatMessage]


class RedisSessionStore:
    """JSON 列表存消息；SET 记录 user 下 session_id 便于列举。"""

    def __init__(self, redis_url: str) -> None:
        import redis

        self._r: Any = redis.from_url(redis_url, decode_responses=True)
        self._lock = threading.Lock()

    @staticmethod
    def ensure_user_id(user_id: str | None) -> str:
        import uuid

        return user_id.strip() if user_id and user_id.strip() else "default"

    @staticmethod
    def ensure_session_id(session_id: str | None) -> str:
        import uuid

        return session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())

    def _load_messages(self, user_id: str, session_id: str) -> list[ChatMessage]:
        raw = self._r.get(_stm_key(user_id, session_id))
        if not raw:
            return []
        try:
            data = json.loads(raw)
            out: list[ChatMessage] = []
            for row in data:
                if isinstance(row, dict) and row.get("role") in ("system", "user", "assistant", "tool"):
                    out.append(ChatMessage(role=row["role"], content=str(row.get("content") or "")))
            return out
        except (json.JSONDecodeError, TypeError):
            return []

    def _save_messages(self, user_id: str, session_id: str, messages: list[ChatMessage]) -> None:
        payload = [{"role": m.role, "content": m.content or ""} for m in messages]
        key = _stm_key(user_id, session_id)
        self._r.set(key, json.dumps(payload, ensure_ascii=False))
        self._r.sadd(_user_index_key(user_id), session_id)

    def get_or_create(self, *, user_id: str, session_id: str) -> SessionState:
        with self._lock:
            msgs = self._load_messages(user_id, session_id)
            return SessionState(user_id=user_id, session_id=session_id, messages=msgs)

    def append(self, *, user_id: str, session_id: str, message: ChatMessage) -> None:
        with self._lock:
            msgs = self._load_messages(user_id, session_id)
            msgs.append(message)
            self._save_messages(user_id, session_id, msgs)

    def reset(self, *, user_id: str, session_id: str) -> bool:
        with self._lock:
            key = _stm_key(user_id, session_id)
            existed = self._r.exists(key) > 0
            if existed:
                self._r.delete(key)
            self._r.srem(_user_index_key(user_id), session_id)
            return bool(existed)

    def list_sessions_for_user(self, user_id: str) -> list[tuple[str, int]]:
        with self._lock:
            sids = list(self._r.smembers(_user_index_key(user_id)) or [])
            out: list[tuple[str, int]] = []
            idx_key = _user_index_key(user_id)
            for sid in sids:
                n = len(self._load_messages(user_id, sid))
                if n > 0:
                    out.append((sid, n))
                else:
                    # 索引里残留但主 key 已丢（外部删 key 等）→ 清理僵尸 session_id
                    self._r.srem(idx_key, sid)
            out.sort(key=lambda x: (-x[1], x[0]))
            return out

    def get_messages(self, *, user_id: str, session_id: str) -> list[ChatMessage] | None:
        with self._lock:
            if not self._r.exists(_stm_key(user_id, session_id)):
                return None
            return self._load_messages(user_id, session_id)

    def clear_all_sessions_for_user(self, user_id: str) -> int:
        with self._lock:
            sids = list(self._r.smembers(_user_index_key(user_id)) or [])
            n = 0
            for sid in sids:
                key = _stm_key(user_id, sid)
                if self._r.exists(key):
                    n += 1
                self._r.delete(key)
            self._r.delete(_user_index_key(user_id))
            return n
