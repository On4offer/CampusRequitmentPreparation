"""
V5 运营热配置：读写 JSON 文件并同步到全局 `settings` 单例，使下一轮 /chat 立即生效。

- 仅允许白名单字段，防止误改 LLM 密钥等敏感项。
- 启动时若存在热配置文件则加载覆盖（在 .env 默认值之上再覆盖）。
"""

from __future__ import annotations

import json
import threading
from pathlib import Path
from typing import Any

from app.core.settings import settings

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
_lock = threading.Lock()

# key -> 期望类型（用于校验）
ALLOWED_KEYS: dict[str, type] = {
    "rag_enabled": bool,
    "rag_top_k": int,
    "rag_min_score": float,
    "rag_max_chars": int,
    "rag_use_hybrid": bool,
    "rag_bm25_top_k": int,
    "rag_rewrite_enabled": bool,
    "rag_rewrite_min_score": float,
    "tool_enabled": bool,
    "quota_enabled": bool,
    "quota_token_per_user_per_day": int,
    "quota_qps_per_user": float,
    "stm_max_chars": int,
    "content_safety_enabled": bool,
    "content_safety_filter_output": bool,
    "feedback_enabled": bool,
    "quota_degrade_on_exhaust": bool,
    "quota_degrade_system_hint": str,
    # V1.1 隐式 LTM：热切换开关与常用门控（不写盘 LLM 密钥）
    "ltm_extract_enabled": bool,
    "ltm_extract_every_n_turns": int,
    "ltm_extract_dedup_enabled": bool,
    "ltm_extract_count_toward_quota": bool,
    "ltm_extract_async": bool,
}


def _resolve_path(rel_or_abs: str) -> Path:
    p = Path(rel_or_abs)
    if p.is_absolute():
        return p
    return _PROJECT_ROOT / p


def _coerce(key: str, raw: Any) -> Any:
    t = ALLOWED_KEYS[key]
    if t is bool:
        if isinstance(raw, bool):
            return raw
        if isinstance(raw, (int, float)):
            return bool(raw)
        if isinstance(raw, str):
            return raw.strip().lower() in ("1", "true", "yes", "on")
        raise TypeError(f"{key} must be bool")
    if t is int:
        v = int(raw)
        if key == "rag_top_k" and not (1 <= v <= 50):
            raise ValueError("rag_top_k must be 1..50")
        if key == "rag_bm25_top_k" and not (1 <= v <= 50):
            raise ValueError("rag_bm25_top_k must be 1..50")
        if key == "rag_max_chars" and not (200 <= v <= 20000):
            raise ValueError("rag_max_chars must be 200..20000")
        if key == "stm_max_chars" and not (500 <= v <= 100_000):
            raise ValueError("stm_max_chars must be 500..100000")
        if key == "quota_token_per_user_per_day" and v < 0:
            raise ValueError("quota_token_per_user_per_day must be >= 0")
        if key == "ltm_extract_every_n_turns" and not (0 <= v <= 20):
            raise ValueError("ltm_extract_every_n_turns must be 0..20 (0 表示不按 assistant 轮次触发)")
        return v
    if t is float:
        v = float(raw)
        if key == "quota_qps_per_user" and not (0 <= v <= 1000):
            raise ValueError("quota_qps_per_user must be 0..1000")
        if key in ("rag_min_score", "rag_rewrite_min_score") and not (0.0 <= v <= 1.0):
            raise ValueError(f"{key} must be 0..1")
        return v
    if t is str:
        if not isinstance(raw, str):
            raise TypeError(f"{key} must be str")
        s = raw.strip()
        if key == "quota_degrade_system_hint" and len(s) > 800:
            raise ValueError("quota_degrade_system_hint max 800 chars")
        return s
    raise TypeError(f"unsupported type for {key}")


def _apply_to_settings(updates: dict[str, Any]) -> None:
    for k, v in updates.items():
        if k not in ALLOWED_KEYS:
            continue
        val = _coerce(k, v)
        object.__setattr__(settings, k, val)


def snapshot_from_settings() -> dict[str, Any]:
    """当前 settings 上白名单字段的快照。"""
    return {k: getattr(settings, k) for k in ALLOWED_KEYS}


def load_hot_config_from_disk() -> dict[str, Any]:
    """
    启动时调用：若热配置文件存在，将其中键应用到 settings。
    返回已应用的键值（仅白名单内）。
    """
    path = _resolve_path(getattr(settings, "hot_config_path", "data/hot_config.json"))
    if not path.exists():
        return {}
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(raw, dict):
        return {}
    to_apply: dict[str, Any] = {}
    for k, v in raw.items():
        if k not in ALLOWED_KEYS:
            continue
        try:
            to_apply[k] = _coerce(k, v)
        except (TypeError, ValueError):
            continue
    if to_apply:
        with _lock:
            _apply_to_settings(to_apply)
    return to_apply


def merge_patch(updates: dict[str, Any]) -> dict[str, Any]:
    """
    合并 PATCH：校验 -> 与磁盘已有 JSON 合并 -> 写盘 -> 应用到 settings。
    返回合并后的完整白名单快照。
    """
    path = _resolve_path(getattr(settings, "hot_config_path", "data/hot_config.json"))
    current_file: dict[str, Any] = {}
    if path.exists():
        try:
            loaded = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                current_file = {k: v for k, v in loaded.items() if k in ALLOWED_KEYS}
        except (OSError, json.JSONDecodeError):
            current_file = {}

    merged = {**current_file}
    for k, v in updates.items():
        if k not in ALLOWED_KEYS:
            raise ValueError(f"unknown or disallowed config key: {k}")
        merged[k] = _coerce(k, v)

    with _lock:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(merged, ensure_ascii=False, indent=2), encoding="utf-8")
        _apply_to_settings(merged)

    return snapshot_from_settings()
