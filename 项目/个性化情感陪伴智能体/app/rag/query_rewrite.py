"""
V4 Query 改写/重试：首次召回弱时用 LLM 改写 query 再检索。

典型 Agentic RAG 思路：用户表达口语化/隐含时，改写为更利于检索的关键词形式。
"""

from __future__ import annotations

import asyncio

from app.llm.client import ChatMessage, LLMClient


REWRITE_SYSTEM_PROMPT = """你是一个检索查询改写助手。任务：将用户的自然语言表达改写成更适合检索长期记忆的简短关键词形式。

要求：
- 输出仅包含改写后的检索词，不要解释、不要引号
- 提取偏好、禁忌、称呼、重要事实等关键信息
- 若用户说「别鸡汤」「不要讲道理」→ 输出「不要鸡汤 不要讲道理」
- 若用户说「叫我小张」→ 输出「称呼小张」
- 保持简短，20 字以内"""


async def rewrite_for_retrieval(
    query: str,
    llm: LLMClient,
    *,
    timeout_s: float = 5.0,
) -> str | None:
    """
    将用户 query 改写为检索友好形式。

    返回改写后的 query，失败或超时时返回 None（调用方降级为原 query）。
    """
    if not (query or "").strip():
        return None

    messages = [
        ChatMessage(role="system", content=REWRITE_SYSTEM_PROMPT),
        ChatMessage(role="user", content=f"用户说：{query.strip()}\n\n请输出改写后的检索词："),
    ]

    try:
        resp = await asyncio.wait_for(llm.chat(messages, temperature=0.3), timeout=timeout_s)
        rewritten = LLMClient.extract_text(resp).strip()
        if rewritten and len(rewritten) < 200:
            return rewritten
        return None
    except (asyncio.TimeoutError, Exception):
        return None
