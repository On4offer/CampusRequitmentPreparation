from __future__ import annotations

"""
LLM 客户端封装层（OpenAI 兼容协议）。

本项目选择“兼容 OpenAI ChatCompletions”作为适配层，原因：
- DeepSeek/通义/百炼等通常提供 OpenAI 兼容接口，迁移成本低
- 业务侧只关心 messages 输入与文本输出，尽量隔离供应商差异
"""

import uuid
from dataclasses import dataclass
from typing import Any, Literal

import httpx


# 角色
Role = Literal["system", "user", "assistant", "tool"]


# @dataclass注解：用于定义数据类（数据容器），自动生成 __init__、__repr__、__eq__ 等方法。
@dataclass(frozen=True)
class ChatMessage:
    """对话消息的最小数据结构（角色 + 文本内容）。"""

    role: Role
    content: str


class LLMClientError(RuntimeError):
    """与大模型服务交互失败时抛出的异常（网络/HTTP/协议解析等）。"""

    pass


class LLMClient:
    """
    最小可用的 OpenAI 兼容 ChatCompletions 客户端。

    约定的接口形态：
    - POST {base_url}/v1/chat/completions

    设计取舍：
    - 只实现本项目当前需要的字段（model/messages/temperature）
    - 将供应商差异（base_url、model、key）收敛到初始化参数
    """

    # 构造函数，作用是初始化成员变量，并返回实例对象。
    # *, 后面的参数必须通过参数名传递
    def __init__(self, *, base_url: str, api_key: str, model: str, timeout_s: float = 60.0):
        """
        初始化 LLM 客户端。

        - base_url: OpenAI 兼容服务的 base url（不带 /v1）
        - api_key: 访问密钥
        - model: 模型名（如 deepseek-chat）
        - timeout_s: HTTP 超时（秒）
        """

        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_s

    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.7) -> dict[str, Any]:
        """
        调用 ChatCompletions 接口。

        - messages: 完整对话上下文（含 system/history/user）
        - temperature: 生成随机性

        返回：
        - dict 包含 request_id（便于排障）与 raw（原始响应 JSON）
        """

        request_id = str(uuid.uuid4())
        url = f"{self._base_url}/v1/chat/completions"
        payload = {
            "model": self._model,
            "messages": [{"role": m.role, "content": m.content} for m in messages],
            "temperature": temperature,
        }
        headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

        # 发起 HTTP 请求, 并处理异常, 解析 JSON 响应, 检查 HTTP 状态码, 若异常则抛出 LLMClientError 异常。
        # async with 语句：用于异步上下文管理，确保在使用完资源后及时关闭连接，避免资源泄漏。
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                # await 关键字：用于等待异步操作完成，确保在继续执行后续代码之前，异步操作已经完成。
                # post 函数：用于发送 POST 请求，并返回响应对象。
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.HTTPError as e:
                raise LLMClientError(f"LLM request failed ({request_id}): {e}") from e

        if resp.status_code >= 400:
            raise LLMClientError(
                f"LLM http {resp.status_code} ({request_id}): {resp.text[:1000]}"   # f 字符串格式化
            )

        data = resp.json()
        return {"request_id": request_id, "raw": data}

    @staticmethod   # 静态方法，不依赖实例状态，可直接通过类名调用。
    def extract_text(chat_response: dict[str, Any]) -> str:
        """
        从 OpenAI 风格响应中提取 assistant 文本。

        若响应结构异常，返回空字符串（上层再做兜底/报错）。
        """

        # raw 为字典，choices 为列表，每个元素为字典，message 为字典，content 为字符串。
        raw = chat_response.get("raw") or {}
        try:
            return raw["choices"][0]["message"]["content"] or ""
        except Exception:
            return ""

