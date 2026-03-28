from __future__ import annotations

"""
Trace 存储层（Day3）。

这里采用“文件落盘”方案：
- 每个 trace_id 对应一个 json 文件：trace_dir/<trace_id>.json
- 另外维护一个 append-only 的 index.jsonl（便于按 session_id 列表查询）

优点：
- 实现简单、零外部依赖、便于演示（打开文件就能看到链路）
- `GET /trace/{trace_id}` O(1) 读取单文件

缺点：
- 大规模/高并发时不够高效（后续可替换为 SQLite/Redis/ES 等）
"""

import json
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from app.trace.models import TraceRecord


class TraceStore(Protocol):
    """TraceStore 抽象：便于后续替换存储实现（文件/SQLite/Redis）。"""

    def put(self, record: TraceRecord) -> None: ...

    def get(self, trace_id: str) -> TraceRecord | None: ...

    def list_by_session(self, *, user_id: str, session_id: str, limit: int = 20) -> list[TraceRecord]: ...


def _safe_mkdir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


@dataclass(frozen=True)
class FileTraceStore:
    """
    文件存储实现。

    - trace_dir: 存放单条 trace json 文件的目录
    - index_file: 记录 trace 元信息的 jsonl（便于列表查询）
    """

    trace_dir: Path
    index_file: Path

    def put(self, record: TraceRecord) -> None:
        _safe_mkdir(self.trace_dir)
        _safe_mkdir(self.index_file.parent)

        trace_path = self.trace_dir / f"{record.trace_id}.json"
        trace_path.write_text(
            json.dumps(record.model_dump(mode="json"), ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )

        # index 只存最小字段，避免文件过大
        index_row = {
            "trace_id": record.trace_id,
            "user_id": record.request.user_id,
            "session_id": record.request.session_id,
            "timestamp_ms": record.request.timestamp_ms,
        }
        with self.index_file.open("a", encoding="utf-8") as f:
            f.write(json.dumps(index_row, ensure_ascii=False) + "\n")

    def get(self, trace_id: str) -> TraceRecord | None:
        trace_path = self.trace_dir / f"{trace_id}.json"
        if not trace_path.exists():
            return None
        raw = trace_path.read_text(encoding="utf-8")
        return TraceRecord.model_validate_json(raw)

    def list_by_session(self, *, user_id: str, session_id: str, limit: int = 20) -> list[TraceRecord]:
        """
        按 user_id + session_id 列出最近 N 条 trace。

        说明：
        - 这里从 index.jsonl 末尾向前扫描（简单但足够用）
        - 大规模时建议换 SQLite/ES 或维护更强的索引结构
        """

        if limit <= 0:
            return []
        if not self.index_file.exists():
            return []

        # 简化实现：读取全部 index 再倒序过滤（本地演示通常足够）
        lines = self.index_file.read_text(encoding="utf-8").splitlines()
        out: list[TraceRecord] = []
        for line in reversed(lines):
            try:
                row = json.loads(line)
            except Exception:
                continue
            if row.get("user_id") != user_id or row.get("session_id") != session_id:
                continue
            rec = self.get(row.get("trace_id", ""))
            if rec is not None:
                out.append(rec)
            if len(out) >= limit:
                break
        return out


class InMemoryTraceStore:
    """内存版 trace store：主要用于 pytest（不写磁盘，速度快、无副作用）。"""

    def __init__(self) -> None:
        self._by_id: dict[str, TraceRecord] = {}
        self._by_session: dict[tuple[str, str], list[str]] = {}

    def put(self, record: TraceRecord) -> None:
        self._by_id[record.trace_id] = record
        key = (record.request.user_id, record.request.session_id)
        self._by_session.setdefault(key, []).append(record.trace_id)

    def get(self, trace_id: str) -> TraceRecord | None:
        return self._by_id.get(trace_id)

    def list_by_session(self, *, user_id: str, session_id: str, limit: int = 20) -> list[TraceRecord]:
        key = (user_id, session_id)
        ids = self._by_session.get(key, [])
        out: list[TraceRecord] = []
        for tid in reversed(ids):
            rec = self._by_id.get(tid)
            if rec is not None:
                out.append(rec)
            if len(out) >= limit:
                break
        return out


def default_file_store() -> FileTraceStore:
    """
    默认文件落盘目录。

    注意：这里不直接依赖 settings，避免 import 顺序/循环依赖；
    上层在启动时可替换 store 实现（例如测试使用 InMemoryTraceStore）。
    """

    # 这里使用 settings.trace_dir（可配），并尽量转成绝对路径，避免 IDE 工作目录差异导致“写到奇怪的位置”
    from app.core.settings import settings

    root = Path(os.getcwd())
    trace_dir = Path(settings.trace_dir)
    if not trace_dir.is_absolute():
        trace_dir = root / trace_dir
    index_file = trace_dir / "index.jsonl"
    return FileTraceStore(trace_dir=trace_dir, index_file=index_file)


def now_ms() -> int:
    """当前时间戳（毫秒）。"""

    return int(time.time() * 1000)

