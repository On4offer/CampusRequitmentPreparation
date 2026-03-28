from __future__ import annotations

import json
import time
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

Window = Literal["day", "week"]


def load_emotion_jsonl(path: str, max_lines: int) -> list[dict[str, Any]]:
    """从 JSONL 尾部读取最多 max_lines 条可解析行（全文件过大时截尾）。"""
    p = Path(path)
    if not p.is_file():
        return []
    try:
        raw = p.read_text(encoding="utf-8")
    except OSError:
        return []
    lines = raw.splitlines()
    if len(lines) > max_lines:
        lines = lines[-max_lines:]
    out: list[dict[str, Any]] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out


def _utc_day(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")


def _utc_hour_bucket(ts_ms: int) -> str:
    return datetime.fromtimestamp(ts_ms / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d %H:00")


def compute_emotion_stats(
    records: list[dict[str, Any]],
    *,
    user_id: str,
    window: Window,
    now_ms: int | None = None,
) -> dict[str, Any]:
    """按 user_id 过滤后，在 window 时间窗内聚合。"""
    now_ms = now_ms or int(time.time() * 1000)
    if window == "week":
        start_ms = now_ms - 7 * 86400 * 1000
    else:
        start_ms = now_ms - 86400 * 1000

    filtered: list[dict[str, Any]] = []
    for r in records:
        if (r.get("user_id") or "") != user_id:
            continue
        ts = int(r.get("timestamp_ms") or 0)
        if ts < start_ms:
            continue
        filtered.append(r)

    by_label: dict[str, int] = defaultdict(int)
    by_risk: dict[str, int] = defaultdict(int)
    for r in filtered:
        lab = str(r.get("label") or "未知")
        by_label[lab] += 1
        risk = str(r.get("risk_tier") or "未知")
        by_risk[risk] += 1

    series: list[dict[str, Any]] = []
    if window == "week":
        day_counts: dict[str, int] = defaultdict(int)
        for r in filtered:
            ts = int(r.get("timestamp_ms") or 0)
            day_counts[_utc_day(ts)] += 1
        # 保证时间轴连续 7 天（UTC）
        for i in range(6, -1, -1):
            d = datetime.fromtimestamp((now_ms - i * 86400 * 1000) / 1000.0, tz=timezone.utc).strftime("%Y-%m-%d")
            series.append({"bucket": d, "count": day_counts.get(d, 0)})
    else:
        hour_counts: dict[str, int] = defaultdict(int)
        for r in filtered:
            ts = int(r.get("timestamp_ms") or 0)
            hour_counts[_utc_hour_bucket(ts)] += 1
        # 最近 24 个整点桶（UTC）
        base = (now_ms // 3600000) * 3600000
        for i in range(23, -1, -1):
            ts = base - i * 3600000
            b = _utc_hour_bucket(ts)
            series.append({"bucket": b, "count": hour_counts.get(b, 0)})

    return {
        "record_count": len(filtered),
        "by_label": dict(by_label),
        "by_risk_tier": dict(by_risk),
        "series": series,
        "window": window,
        "window_start_ms": start_ms,
        "window_end_ms": now_ms,
    }
