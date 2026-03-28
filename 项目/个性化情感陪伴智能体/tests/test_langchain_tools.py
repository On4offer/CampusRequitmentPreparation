"""LangChain StructuredTool 与 execute_tool 行为对齐。"""

from __future__ import annotations

from app.langchain.tools_lc import run_policy_tool_via_structured_tool
from app.tools.executor import execute_tool
from app.tools.router import route_tool_params


def test_structured_time_matches_execute_tool():
    params = route_tool_params("time", "现在几点")
    a, ms_a = execute_tool("time", params, timeout_s=5.0, retry_times=1)
    b, ms_b = run_policy_tool_via_structured_tool("time", params, timeout_s=5.0, retry_times=1)
    assert a.success == b.success
    assert (a.raw_text or "") == (b.raw_text or "")


def test_structured_weather_matches_execute_tool():
    params = route_tool_params("weather", "上海天气怎么样")
    a, _ = execute_tool("weather", params, timeout_s=5.0, retry_times=1)
    b, _ = run_policy_tool_via_structured_tool("weather", params, timeout_s=5.0, retry_times=1)
    assert a.success == b.success
    assert (a.raw_text or "") == (b.raw_text or "")


def test_make_lc_tools_for_bind_has_two_tools():
    from app.langchain.tools_lc import make_lc_structured_tools_for_bind

    tools = make_lc_structured_tools_for_bind(timeout_s=5.0, retry_times=1)
    names = {t.name for t in tools}
    assert names == {"time", "weather"}
