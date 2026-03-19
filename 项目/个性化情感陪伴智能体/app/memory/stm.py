from __future__ import annotations

"""
短期记忆（STM）裁剪策略。STM全拼：Short-Term Memory

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
        return []   # 返回空列表，表示不限制字符数
    kept: list[ChatMessage] = []     # 保留的消息列表，kept是保留的消息列表，类型是 ChatMessage
    remaining = max_chars
    for m in reversed(messages):
        c = len(m.content or "")    # 计算消息内容的字符数
        if kept and c > remaining:
            break
        if not kept and c > max_chars:
            # Single message too long: keep tail.
            # 单条消息字符数超过预算，只保留尾部内容
            # 把历史消息 m，裁剪到最多 max_chars 字，然后放进 kept 列表保存。
            kept.append(ChatMessage(role=m.role, content=(m.content or "")[-max_chars:]))
            break
        kept.append(m)
        remaining -= c  # 更新剩余字符数
    # 返回保留的消息列表，按原始顺序
    return list(reversed(kept))

