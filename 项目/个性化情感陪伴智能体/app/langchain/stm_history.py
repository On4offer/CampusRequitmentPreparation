from __future__ import annotations

"""
STM → LangChain BaseChatMessageHistory：读写在自研 session_store 上，裁剪规则与 trim_messages_by_char_budget 一致。
"""

from collections.abc import Sequence

from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage

from app.langchain.messages import chat_messages_to_lc, lc_base_messages_to_chat
from app.llm.client import ChatMessage
from app.memory.stm import trim_messages_by_char_budget
from app.memory.store import session_store


class SessionStoreChatMessageHistory(BaseChatMessageHistory):
    """底层为 `session_store`（内存或 Redis）；`messages` 为裁剪后的 LangChain 消息列表。"""

    def __init__(self, *, user_id: str, session_id: str, max_chars: int) -> None:
        self.user_id = user_id
        self.session_id = session_id
        self.max_chars = max_chars

    def get_trimmed_chat_messages(self) -> list[ChatMessage]:
        state = session_store.get_or_create(user_id=self.user_id, session_id=self.session_id)
        return trim_messages_by_char_budget(state.messages, max_chars=self.max_chars)

    @property
    def messages(self) -> list[BaseMessage]:
        return list(chat_messages_to_lc(self.get_trimmed_chat_messages()))

    def add_messages(self, messages: Sequence[BaseMessage]) -> None:
        for cm in lc_base_messages_to_chat(messages):
            session_store.append(user_id=self.user_id, session_id=self.session_id, message=cm)

    def clear(self) -> None:
        session_store.reset(user_id=self.user_id, session_id=self.session_id)
