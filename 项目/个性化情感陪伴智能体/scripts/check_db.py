"""
简单探测 DATABASE_URL 是否可用（SELECT 1）。

在项目根目录、已激活 venv 时执行：

    python scripts/check_db.py

依赖与主项目相同（sqlalchemy、pymysql 等）；读取根目录 `.env`（与 `app.core.settings` 一致）。
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


def main() -> int:
    from sqlalchemy import create_engine, text

    from app.core.settings import settings

    url = (settings.database_url or "").strip()
    if not url:
        print("DATABASE_URL 未配置（空则不走 MySQL）。")
        return 0

    try:
        engine = create_engine(url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("OK: 数据库连接成功（SELECT 1）。")
        return 0
    except Exception as e:
        print(f"失败: {type(e).__name__}: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
