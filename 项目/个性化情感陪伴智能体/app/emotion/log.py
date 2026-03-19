"""
情绪结果落盘（V1 占位）：为情绪曲线/回访预留。

每轮 /chat 在得到情绪结果后，可选追加一条 JSONL 到指定文件。
字段：user_id, session_id, timestamp_ms, label, intensity, risk_tier, trace_id（与 trace 中 emotion 一致）。
"""

from __future__ import annotations

import json
from pathlib import Path


def append_emotion_record(file_path: str, record: dict) -> None:
    """
    向 JSONL 文件追加一条情绪记录。

    record 建议包含：user_id, session_id, timestamp_ms, label, intensity, risk_tier, trace_id。
    若目录不存在会先创建；写入失败时静默忽略（不打断主链路）。
    """
    try:
        p = Path(file_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")
    except (OSError, TypeError, ValueError):
        pass
