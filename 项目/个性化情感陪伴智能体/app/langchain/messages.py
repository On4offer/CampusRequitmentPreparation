from __future__ import annotations

from collections.abc import Sequence

from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage, ToolMessage

from app.llm.client import ChatMessage


def chat_messages_to_lc(messages: list[ChatMessage]) -> list[SystemMessage | HumanMessage | AIMessage | ToolMessage]:
    out: list[SystemMessage | HumanMessage | AIMessage | ToolMessage] = []
    for m in messages:
        if m.role == "system":
            out.append(SystemMessage(content=m.content))
        elif m.role == "user":
            out.append(HumanMessage(content=m.content))
        elif m.role == "assistant":
            out.append(AIMessage(content=m.content))
        elif m.role == "tool":
            out.append(ToolMessage(content=m.content, tool_call_id="tool"))
    return out


def lc_ai_message_text(content: object) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "text":
                t = block.get("text")
                if isinstance(t, str):
                    parts.append(t)
        return "".join(parts)
    return str(content or "")


def lc_base_messages_to_chat(messages: Sequence[BaseMessage]) -> list[ChatMessage]:
    """LangChain BaseMessage → 项目 ChatMessage（用于 STM 写回等）。"""
    out: list[ChatMessage] = []
    for m in messages:
        if isinstance(m, SystemMessage):
            out.append(ChatMessage(role="system", content=str(m.content or "")))
        elif isinstance(m, HumanMessage):
            out.append(ChatMessage(role="user", content=str(m.content or "")))
        elif isinstance(m, AIMessage):
            out.append(ChatMessage(role="assistant", content=lc_ai_message_text(m.content)))
        elif isinstance(m, ToolMessage):
            out.append(ChatMessage(role="tool", content=str(m.content or "")))
        else:
            out.append(ChatMessage(role="user", content=str(getattr(m, "content", "") or "")))
    return out
