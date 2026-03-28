"""LangChain 回调里解析供应商 request id（与 Trace/SSE 对齐）。"""

from __future__ import annotations

from langchain_core.messages import AIMessage
from langchain_core.outputs import ChatGeneration, LLMResult

from app.langchain.llm_trace_callback import extract_provider_request_id


def test_extract_id_from_chat_generation_metadata():
    r = LLMResult(
        generations=[
            [
                ChatGeneration(
                    message=AIMessage(content="x", response_metadata={"id": "req-abc"}),
                )
            ]
        ],
        llm_output=None,
    )
    assert extract_provider_request_id(r) == "req-abc"


def test_extract_id_from_llm_output_fallback():
    r = LLMResult(
        generations=[[ChatGeneration(message=AIMessage(content="y"), text="y")]],
        llm_output={"id": "from-llm-output"},
    )
    assert extract_provider_request_id(r) == "from-llm-output"


def test_extract_id_prefers_message_over_llm_output():
    r = LLMResult(
        generations=[
            [
                ChatGeneration(
                    message=AIMessage(content="z", response_metadata={"id": "msg-win"}),
                )
            ]
        ],
        llm_output={"id": "output-lose"},
    )
    assert extract_provider_request_id(r) == "msg-win"


def test_extract_id_empty():
    r = LLMResult(
        generations=[[ChatGeneration(message=AIMessage(content="n"), text="n")]],
        llm_output={},
    )
    assert extract_provider_request_id(r) is None
