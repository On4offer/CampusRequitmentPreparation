"""
探测 REDIS_URL 是否可用（PING）。

在项目根目录、已激活 venv 时执行：

    python scripts/check_redis.py

读取根目录 `.env`（与 `app.core.settings` 一致）。
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    from app.core.settings import settings

    url = (settings.redis_url or "").strip()
    if not url:
        print("REDIS_URL 未配置（空则 STM 走进程内内存）。")
        return 0

    try:
        import redis

        r = redis.from_url(url)
        r.ping()
        print("OK: Redis PING 成功。")
        return 0
    except Exception as e:
        print(f"失败: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
