from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Any, Literal

import httpx


Role = Literal["system", "user", "assistant", "tool"]


@dataclass(frozen=True)
class ChatMessage:
    role: Role
    content: str


class LLMClientError(RuntimeError):
    pass


class LLMClient:
    """
    Minimal OpenAI-compatible ChatCompletions client.

    Works with OpenAI-style endpoints:
    - POST {base_url}/v1/chat/completions
    """

    def __init__(self, *, base_url: str, api_key: str, model: str, timeout_s: float = 60.0):
        self._base_url = base_url.rstrip("/")
        self._api_key = api_key
        self._model = model
        self._timeout = timeout_s

    async def chat(self, messages: list[ChatMessage], *, temperature: float = 0.7) -> dict[str, Any]:
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

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            try:
                resp = await client.post(url, json=payload, headers=headers)
            except httpx.HTTPError as e:
                raise LLMClientError(f"LLM request failed ({request_id}): {e}") from e

        if resp.status_code >= 400:
            raise LLMClientError(
                f"LLM http {resp.status_code} ({request_id}): {resp.text[:1000]}"
            )

        data = resp.json()
        return {"request_id": request_id, "raw": data}

    @staticmethod
    def extract_text(chat_response: dict[str, Any]) -> str:
        raw = chat_response.get("raw") or {}
        try:
            return raw["choices"][0]["message"]["content"] or ""
        except Exception:
            return ""

