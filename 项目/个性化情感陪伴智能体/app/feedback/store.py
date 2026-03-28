"""
V5 反馈落盘：JSONL 追加写入，可选镜像到评测样本文件。

线程安全；路径相对项目根解析（与 trace 一致）。
"""

from __future__ import annotations

import json
import threading
import uuid
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_lock = threading.Lock()


def _resolve_path(rel_or_abs: str) -> Path:
    p = Path(rel_or_abs)
    if p.is_absolute():
        return p
    return _PROJECT_ROOT / p


def append_feedback_row(
    row: dict[str, Any],
    *,
    main_path: str,
    eval_path: str | None,
    mirror_to_eval: bool,
) -> tuple[str, bool]:
    """
    追加一行反馈到主 JSONL；若 mirror_to_eval 为 True 则同时追加到评测 JSONL。

    返回 (feedback_id, mirrored_to_eval)。
    """
    fid = str(row.get("id") or uuid.uuid4())
    row = {**row, "id": fid}
    line = json.dumps(row, ensure_ascii=False) + "\n"
    main = _resolve_path(main_path)
    mirrored = False

    with _lock:
        main.parent.mkdir(parents=True, exist_ok=True)
        with main.open("a", encoding="utf-8") as f:
            f.write(line)
        if mirror_to_eval and eval_path:
            ep = _resolve_path(eval_path)
            ep.parent.mkdir(parents=True, exist_ok=True)
            with ep.open("a", encoding="utf-8") as ef:
                ef.write(line)
            mirrored = True

    return fid, mirrored


def read_feedback_tail(*, path: str, limit: int = 50, user_id: str | None = None) -> list[dict[str, Any]]:
    """从 JSONL 末尾读取最近若干条（全读入内存后过滤，演示规模足够）。"""
    if limit <= 0:
        return []
    p = _resolve_path(path)
    if not p.exists():
        return []
    lines = p.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in reversed(lines):
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if user_id is not None and obj.get("user_id") != user_id:
            continue
        out.append(obj)
        if len(out) >= limit:
            break
    out.reverse()
    return out


def read_feedback_all_for_user(*, path: str, user_id: str) -> list[dict[str, Any]]:
    """读取反馈 JSONL 中属于某用户的全部行（合规导出；规模按演示集可控）。"""
    p = _resolve_path(path)
    if not p.exists():
        return []
    out: list[dict[str, Any]] = []
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError:
        return []
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict) and obj.get("user_id") == user_id:
            out.append(obj)
    return out
