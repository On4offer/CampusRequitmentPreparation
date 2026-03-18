from __future__ import annotations

"""
会话/短期记忆的存储层（Day2）。

当前版本为“进程内存”实现：
- 优点：简单、零依赖、便于快速迭代
- 缺点：服务重启即丢失；多进程/多实例之间不共享

后续若要工程化上线，可将该 Store 替换为 Redis/数据库实现。
"""

import threading
import uuid
from dataclasses import dataclass

from app.llm.client import ChatMessage


@dataclass
class SessionState:
    """单个会话的状态：用户标识、会话标识、以及累积的对话消息列表。"""

    user_id: str
    session_id: str
    messages: list[ChatMessage]


class InMemorySessionStore:
    """
    基于 dict 的会话存储。

    key = (user_id, session_id)
    value = SessionState（包含 messages）
    """

    def __init__(self) -> None:
        """初始化线程安全的 session 容器。"""

        self._lock = threading.Lock()
        self._sessions: dict[tuple[str, str], SessionState] = {}

    @staticmethod
    def ensure_user_id(user_id: str | None) -> str:
        """
        规范化 user_id。

        - None/空串 → "default"（便于快速演示；生产环境建议接入登录体系）
        """

        return user_id.strip() if user_id and user_id.strip() else "default"

    @staticmethod
    def ensure_session_id(session_id: str | None) -> str:
        """
        规范化 session_id。

        - None/空串 → 自动生成 UUID
        """

        return session_id.strip() if session_id and session_id.strip() else str(uuid.uuid4())

    def get_or_create(self, *, user_id: str, session_id: str) -> SessionState:
        """
        获取或创建会话状态。

        返回的 SessionState.messages 会在后续 append 中被持续追加。
        """

        key = (user_id, session_id)
        with self._lock:
            state = self._sessions.get(key)
            if state is None:
                state = SessionState(user_id=user_id, session_id=session_id, messages=[])
                self._sessions[key] = state
            return state

    def append(self, *, user_id: str, session_id: str, message: ChatMessage) -> None:
        """向指定会话追加一条消息（user 或 assistant）。"""

        key = (user_id, session_id)
        with self._lock:
            state = self._sessions.get(key)
            if state is None:
                state = SessionState(user_id=user_id, session_id=session_id, messages=[])
                self._sessions[key] = state
            state.messages.append(message)

    def reset(self, *, user_id: str, session_id: str) -> bool:
        """
        清空指定会话（删除整个 SessionState）。

        返回：
        - existed: 该会话是否原本存在
        """

        key = (user_id, session_id)
        with self._lock:
            existed = key in self._sessions
            if existed:
                del self._sessions[key]
            return existed


session_store = InMemorySessionStore()  
# 类是InMemorySessionStore，实例是session_store，和Java相比，Python的类实例化后，对象名就是实例名
# 类是模板，实例是具体的对象，每个实例都有自己的状态和行为
# Java 命名规范是驼峰命名法，而Python的命名规范是下划线命名法
# 同时不需要new 关键字

