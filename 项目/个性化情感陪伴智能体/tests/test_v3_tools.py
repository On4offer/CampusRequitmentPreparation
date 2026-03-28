"""
V3 工具调用测试：time/weather 工具、trace、降级、tool_enabled 开关。
"""

from __future__ import annotations

import asyncio
from fastapi.testclient import TestClient

from app.main import app
from app.core import settings as core_settings
from app.trace.store import InMemoryTraceStore


class _FakeLLM:
    async def chat(self, messages, temperature: float = 0.7):
        await asyncio.sleep(0)
        content = ""
        for m in messages:
            c = getattr(m, "content", None) or ""
            if c:
                content = c
                break
        if "情绪识别" in content:
            return {"request_id": "e", "raw": {"choices": [{"message": {"content": "ok"}}]}}
        if "工具调用结果" in content or "当前时间" in content:
            return {
                "request_id": "c",
                "raw": {"choices": [{"message": {"content": "当前是下午3点，有什么需要帮忙的吗？"}}]},
            }
        if "天气" in content or "晴" in content:
            return {
                "request_id": "c",
                "raw": {"choices": [{"message": {"content": "西安今天晴，18度，适合出门。"}}]},
            }
        return {"request_id": "c", "raw": {"choices": [{"message": {"content": "好的。"}}]}}

    @staticmethod
    def extract_text(chat_response):
        return chat_response["raw"]["choices"][0]["message"]["content"]


def test_tool_time_success(monkeypatch):
    """开启 tool_enabled 时，问「现在几点」触发 time 工具，返回 200，trace 含 tool_route/tool_execute。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "tool_enabled", True)
    monkeypatch.setattr(core_settings.settings, "tool_timeout_s", 5.0)
    monkeypatch.setattr(core_settings.settings, "tool_retry_times", 1)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "现在几点", "user_id": "u_v3", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("tool_summary") is not None
    assert data["tool_summary"].get("tool") == "time"
    assert data["tool_summary"].get("status") == "success"

    tr = client.get(f"/trace/{data['trace_id']}").json()
    steps_names = [s["name"] for s in tr["steps"]]
    assert "tool_route" in steps_names
    assert "tool_execute" in steps_names
    assert tr.get("decision", {}).get("tool_selected") == "time"
    assert tr.get("decision", {}).get("tool_status") == "success"


def test_tool_weather_success(monkeypatch):
    """开启 tool_enabled 时，问「西安天气」触发 weather 工具。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "tool_enabled", True)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "今天西安天气怎么样", "user_id": "u_v3", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("tool_summary") is not None
    assert data["tool_summary"].get("tool") == "weather"
    assert data["tool_summary"].get("status") == "success"
    tr = client.get(f"/trace/{data['trace_id']}").json()
    assert tr.get("decision", {}).get("tool_selected") == "weather"


def test_tool_disabled_no_execution(monkeypatch):
    """tool_enabled=false 时，问「现在几点」不执行工具，无 tool_summary。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "tool_enabled", False)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "现在几点", "user_id": "u_v3", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("tool_summary") is None
    tr = client.get(f"/trace/{data['trace_id']}").json()
    steps_names = [s["name"] for s in tr["steps"]]
    assert "tool_route" not in steps_names
    assert "tool_execute" not in steps_names


def test_non_tool_message_no_summary(monkeypatch):
    """闲聊消息不触发工具，无 tool_summary。"""
    import app.api.routes as routes

    monkeypatch.setattr(core_settings.settings, "tool_enabled", True)
    monkeypatch.setattr(routes, "_build_llm_client", lambda: _FakeLLM())
    monkeypatch.setattr(routes, "trace_store", InMemoryTraceStore())

    client = TestClient(app)
    r = client.post("/chat", json={"message": "你好呀", "user_id": "u_v3", "session_id": "s1"})
    assert r.status_code == 200
    data = r.json()
    assert data.get("tool_summary") is None


def test_registry_and_executor():
    """工具注册与执行：注册 -> 查询 -> 调用 最小闭环。"""
    from app.tools import tool_registry, execute_tool

    assert "time" in tool_registry.list_tools()
    assert "weather" in tool_registry.list_tools()
    result, elapsed = execute_tool("time", {})
    assert result.success
    assert result.raw_text is not None
    assert "当前时间" in result.raw_text or ":" in result.raw_text

    result, _ = execute_tool("weather", {"city": "北京"})
    assert result.success
    assert "北京" in (result.raw_text or "")

    result, _ = execute_tool("unknown_tool", {})
    assert not result.success
    assert result.error is not None
    assert "未注册" in result.error.message
