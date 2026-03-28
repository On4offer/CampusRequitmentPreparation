"""
按 user_id 的 QPS 与按日「字符预算」（近似 token）计数。

- 日界按 UTC 日期字符串，与本地日略有差异可接受。
- 0 表示不限制。
"""

from __future__ import annotations

import threading
import time
from collections import deque
from datetime import datetime, timezone

# 情绪识别一次 LLM 的粗略字符量（入+出）
EMOTION_CHARS_ESTIMATE = 800

_lock = threading.Lock()
# (user_id, date_utc) -> 累计字符量（近似 token）
_daily_chars: dict[tuple[str, str], int] = {}
# user_id -> deque of monotonic timestamps (last 1s window)
_qps_ts: dict[str, deque[float]] = {}


def _today_key() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_daily_usage(user_id: str) -> int:
    """当前 UTC 日已计入的字符量。"""
    with _lock:
        return int(_daily_chars.get((user_id, _today_key()), 0))


def consume_emotion_estimate(user_id: str) -> None:
    """情绪识别完成后计入估算消耗。"""
    key = (user_id, _today_key())
    with _lock:
        _daily_chars[key] = _daily_chars.get(key, 0) + EMOTION_CHARS_ESTIMATE


def check_token_budget_before_main_llm(
    user_id: str,
    *,
    main_prompt_chars: int,
    reply_estimate: int = 400,
    limit_per_day: int,
) -> tuple[bool, int, int]:
    """
    主 LLM 调用前检查是否仍会超过日预算。

    返回 (allowed, used_so_far, limit)。limit<=0 视为不限制。
    """
    if limit_per_day <= 0:
        return True, get_daily_usage(user_id), 0
    used = get_daily_usage(user_id)
    need = main_prompt_chars + reply_estimate
    if used + need > limit_per_day:
        return False, used, limit_per_day
    return True, used, limit_per_day


def consume_main_llm_usage(user_id: str, token_in_est: int, token_out_est: int) -> None:
    """主 LLM 成功后计入实际估算字符量。"""
    key = (user_id, _today_key())
    with _lock:
        _daily_chars[key] = _daily_chars.get(key, 0) + int(token_in_est) + int(token_out_est)


def check_qps(user_id: str, *, max_per_second: float) -> bool:
    """是否允许本秒再发一次请求。max_per_second<=0 不限制。"""
    if max_per_second <= 0:
        return True
    n = int(max_per_second)
    if n < 1:
        n = 1
    now = time.monotonic()
    cutoff = now - 1.0
    with _lock:
        dq = _qps_ts.setdefault(user_id, deque())
        while dq and dq[0] < cutoff:
            dq.popleft()
        if len(dq) >= n:
            return False
        dq.append(now)
        return True


def reset_for_tests() -> None:
    """测试用：清空计数。"""
    with _lock:
        _daily_chars.clear()
        _qps_ts.clear()


def seed_daily_usage_for_tests(user_id: str, chars: int) -> None:
    """测试用：将当前 UTC 日该用户的已用量设为 chars（覆盖，不叠加）。"""
    key = (user_id, _today_key())
    with _lock:
        _daily_chars[key] = max(0, int(chars))
