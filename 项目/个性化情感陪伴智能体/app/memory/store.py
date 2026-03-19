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

    def __init__(self) -> None: # 初始化，创建一个空的会话存储
        """初始化线程安全的 session 容器。"""

        self._lock = threading.Lock()   # 线程锁，确保线程安全
        # session 容器，key 是 (user_id, session_id)，value 是 SessionState 实例
        self._sessions: dict[tuple[str, str], SessionState] = {}

    @staticmethod   # 静态方法，不依赖实例状态
    def ensure_user_id(user_id: str | None) -> str:
        """
        规范化 user_id。

        - None/空串 → "default"（便于快速演示；生产环境建议接入登录体系）
        """
        # 处理 None/空串情况，返回 "default"
        # 去掉首尾空格，确保 user_id 是一个非空字符串
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
        with self._lock:    # 获取锁，确保线程安全，防止多个线程同时修改 session 容器
            state = self._sessions.get(key) # 获取指定 key 的 SessionState
            if state is None: # 如果不存在，创建一个新的 SessionState
                # 初始化一个空的 SessionState，包含用户 ID、会话 ID、以及空的消息列表
                state = SessionState(user_id=user_id, session_id=session_id, messages=[])
                self._sessions[key] = state # 存储新的 SessionState 到容器中
            return state # 返回 SessionState 实例

    def append(self, *, user_id: str, session_id: str, message: ChatMessage) -> None:
        """向指定会话追加一条消息（user 或 assistant）。"""

        key = (user_id, session_id) # 会话的唯一标识，由用户 ID 和会话 ID 组成
        with self._lock:    # 获取锁，确保线程安全，防止多个线程同时修改 session 容器
            state = self._sessions.get(key) # 获取指定 key 的 SessionState
            if state is None: # 如果不存在，创建一个新的 SessionState
                state = SessionState(user_id=user_id, session_id=session_id, messages=[])
                self._sessions[key] = state # 存储新的 SessionState 到容器中
            state.messages.append(message) # 追加新消息到会话历史


    def reset(self, *, user_id: str, session_id: str) -> bool:
        """
        清空指定会话（删除整个 SessionState）。

        返回：
        - existed: 该会话是否原本存在
        """

        key = (user_id, session_id) # 会话的唯一标识，由用户 ID 和会话 ID 组成
        with self._lock:    # 获取锁，确保线程安全，防止多个线程同时修改 session 容器
            existed = key in self._sessions # 检查会话是否存在
            if existed:
                del self._sessions[key] # 删除会话
            return existed # 返回会话是否存在结果


session_store = InMemorySessionStore()  
# 类是InMemorySessionStore，实例是session_store，和Java相比，Python的类实例化后，对象名就是实例名
# 类是模板，实例是具体的对象，每个实例都有自己的状态和行为
# Java 命名规范是驼峰命名法，而Python的命名规范是下划线命名法
# 同时不需要new 关键字

