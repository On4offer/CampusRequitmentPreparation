"""SQLLTMStore.list_by_user：COUNT + LIMIT/OFFSET，避免全表拉入内存（V1.1 可选 B3）。"""

from __future__ import annotations

import time

from app.memory.ltm import LTMItem
from app.memory.ltm_sql import SQLLTMStore, init_ltm_db


def test_sql_ltm_list_pagination_and_total(tmp_path):
    url = f"sqlite:///{tmp_path / 'ltm_page.db'}"
    init_ltm_db(url)
    store = SQLLTMStore(url)
    uid = "u_sql_ltm_page"
    base_ts = int(time.time() * 1000)
    for i in range(5):
        store.put(
            uid,
            LTMItem(
                user_id=uid,
                type="Profile",
                content=f"条目{i}",
                created_at=base_ts + i,
            ),
        )

    p0, total0 = store.list_by_user(uid, limit=2, offset=0)
    assert total0 == 5
    assert len(p0) == 2

    p1, total1 = store.list_by_user(uid, limit=2, offset=4)
    assert total1 == 5
    assert len(p1) == 1


def test_sql_ltm_list_query_filter_total(tmp_path):
    url = f"sqlite:///{tmp_path / 'ltm_q.db'}"
    init_ltm_db(url)
    store = SQLLTMStore(url)
    uid = "u_sql_q"
    ts = int(time.time() * 1000)
    store.put(uid, LTMItem(user_id=uid, type="Event", content="苹果", created_at=ts))
    store.put(uid, LTMItem(user_id=uid, type="Event", content="香蕉", created_at=ts + 1))

    items, total = store.list_by_user(uid, q="苹", limit=10, offset=0)
    assert total == 1
    assert len(items) == 1
    assert "苹" in items[0].content
