"""单测共用：主对话走 LangChain ChatModel mock；情绪/隐式 LTM 仍 monkeypatch `routes._build_llm_client`。"""

from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

import pytest
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult

import app.api.routes as routes

LC_MAIN_REPLY = "好的，我在这里。"


class FakeLCMainChatModel(BaseChatModel):
    """与 `build_chat_openai_from_settings` 对齐的最小 ChatModel（非流式 + 流式）。"""

    def _llm_type(self) -> str:
        return "tests-fake-lc-main"

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs: object,
    ) -> ChatResult:
        return ChatResult(
            generations=[
                ChatGeneration(
                    message=AIMessage(content=LC_MAIN_REPLY, response_metadata={"id": "lc-json-id"}),
                )
            ]
        )

    async def _astream(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager=None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGenerationChunk]:
        yield ChatGenerationChunk(message=AIMessageChunk(content=LC_MAIN_REPLY))


def patch_llm_client(monkeypatch: pytest.MonkeyPatch, fake_llm: object) -> None:
    """仅替换 httpx LLMClient（情绪、隐式抽取等）；主对话由 conftest 对 ChatOpenAI 的 mock 覆盖。"""
    monkeypatch.setattr(routes, "_build_llm_client", lambda: fake_llm)
