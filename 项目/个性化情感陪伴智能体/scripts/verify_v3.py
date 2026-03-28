"""
V3 工具调用演示脚本：
1. time 成功：现在几点
2. weather 成功：西安天气
3. weather 失败降级：工具超时/参数错时仍返回 200，trace 标记 degraded

运行前需启动后端，且 TOOL_ENABLED=true：
  python -m uvicorn app.main:app --host 127.0.0.1 --port 8076
  TOOL_ENABLED=true python scripts/verify_v3.py http://127.0.0.1:8076
"""

from __future__ import annotations

import json
import sys
import urllib.request


def post(base: str, path: str, body: dict) -> dict:
    req = urllib.request.Request(
        base + path,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get(base: str, path: str) -> dict:
    req = urllib.request.Request(base + path, method="GET")
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8076"
    print("Base:", base)
    print()

    # 1. time 成功
    print("=== 1. time 工具（现在几点）===")
    r1 = post(base, "/chat", {"message": "现在几点", "user_id": "u_v3", "session_id": "s1"})
    print("reply:", r1.get("reply", "")[:200])
    print("tool_summary:", r1.get("tool_summary"))
    trace_id = r1.get("trace_id")
    if trace_id:
        t = get(base, f"/trace/{trace_id}")
        steps = [s["name"] for s in t.get("steps", [])]
        print("trace steps:", steps)
        print("decision.tool_selected:", t.get("decision", {}).get("tool_selected"))
        print("decision.tool_status:", t.get("decision", {}).get("tool_status"))
    print()

    # 2. weather 成功
    print("=== 2. weather 工具（西安天气）===")
    r2 = post(base, "/chat", {"message": "今天西安天气怎么样", "user_id": "u_v3", "session_id": "s1"})
    print("reply:", r2.get("reply", "")[:200])
    print("tool_summary:", r2.get("tool_summary"))
    if r2.get("trace_id"):
        t = get(base, f"/trace/{r2['trace_id']}")
        print("decision.tool_selected:", t.get("decision", {}).get("tool_selected"))
        print("decision.tool_status:", t.get("decision", {}).get("tool_status"))
    print()

    # 3. 非工具场景（应无 tool_summary）
    print("=== 3. 非工具场景（闲聊）===")
    r3 = post(base, "/chat", {"message": "你好呀", "user_id": "u_v3", "session_id": "s1"})
    print("reply:", r3.get("reply", "")[:100])
    print("tool_summary:", r3.get("tool_summary"))
    print()

    print("Done. 若 tool_summary 为 None，请确认 TOOL_ENABLED=true 并重启后端。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
