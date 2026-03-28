from __future__ import annotations

"""
主对话 LCEL：`ChatPromptTemplate` + `MessagesPlaceholder` → `ChatModel` → `StrOutputParser`。
供应商 `response_metadata.id` 由 `LlmProviderIdCallback`（`on_llm_end`）写入 Trace / SSE，见 `llm_trace_callback.py`。
"""

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import Runnable


def build_main_chat_lc_chain(model: BaseChatModel) -> Runnable:
    """输入：`{"messages": list[BaseMessage]}`；输出：助手纯文本 `str`。"""
    prompt = ChatPromptTemplate.from_messages([MessagesPlaceholder(variable_name="messages")])
    return prompt | model | StrOutputParser()
