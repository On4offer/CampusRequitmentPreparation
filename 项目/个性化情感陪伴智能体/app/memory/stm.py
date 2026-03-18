from __future__ import annotations

"""
短期记忆（STM）裁剪策略。

说明：
- 这里用“字符数预算”做近似裁剪（不精确等价于 token，但实现简单、可用）
- 真实生产可替换为 token 计数、摘要压缩、或多级缓存策略
"""

from app.llm.client import ChatMessage


def trim_messages_by_char_budget(messages: list[ChatMessage], *, max_chars: int) -> list[ChatMessage]:
    """
    按字符数预算保留“最近”的对话消息。

    - messages: 会话历史消息（不包含 system prompt）
    - max_chars: 粗略字符预算，超过则从更早的消息开始丢弃

    返回：
    - 裁剪后的 messages（按原始顺序）

    设计取舍：
    - 为了简单与稳定，不在此处处理 system prompt；system 由上层统一注入
    """
    if max_chars <= 0:
        return []
    kept: list[ChatMessage] = []
    remaining = max_chars
    for m in reversed(messages):
        c = len(m.content or "")
        if kept and c > remaining:
            break
        if not kept and c > max_chars:
            # Single message too long: keep tail.
            kept.append(ChatMessage(role=m.role, content=(m.content or "")[-max_chars:]))
            break
        kept.append(m)
        remaining -= c
    return list(reversed(kept))

