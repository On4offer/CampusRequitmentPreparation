from __future__ import annotations

"""
One-shot Day2 verification (end-to-end):
- multi-turn session memory
- session isolation
- /sessions/reset

Run:
  python scripts/verify_day2.py http://127.0.0.1:8077
"""

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
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode("utf-8"))


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8077"
    CHAT_PATH = "/chat"
    RESET_PATH = "/sessions/reset"
    Q_NAME = "我叫什么？"

    print("Base:", base)

    post(base, CHAT_PATH, {"user_id": "u1", "session_id": "s1", "message": "我叫小明，请记住我。"})
    r2 = post(base, CHAT_PATH, {"user_id": "u1", "session_id": "s1", "message": Q_NAME})
    r3 = post(base, CHAT_PATH, {"user_id": "u1", "session_id": "s2", "message": Q_NAME})
    rr = post(base, RESET_PATH, {"user_id": "u1", "session_id": "s1"})
    r4 = post(base, CHAT_PATH, {"user_id": "u1", "session_id": "s1", "message": Q_NAME})

    print("s1 turn2 reply:", r2.get("reply", "")[:120])
    print("s2 reply:", r3.get("reply", "")[:120])
    print("reset:", rr)
    print("s1 after reset reply:", r4.get("reply", "")[:120])

    print("\nDone.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

