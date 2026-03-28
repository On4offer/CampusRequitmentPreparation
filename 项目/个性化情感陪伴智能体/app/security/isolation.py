"""
V5 用户隔离：校验调用方 user_id 与资源归属一致。

- strict_user_isolation=True：敏感接口必须带 user_id，且与资源一致。
- strict_user_isolation=False：未传 user_id 时保持兼容；若传了则必须一致，否则 403。
"""

from __future__ import annotations

from fastapi import HTTPException

from app.core.settings import settings
from app.memory.ltm import LTMItem
from app.memory.store import session_store
from app.trace.models import TraceRecord


def _norm(uid: str | None) -> str:
    return session_store.ensure_user_id(uid)


def require_user_id_for_strict_mode(caller_user_id: str | None, *, resource: str) -> str:
    """
    严格模式下要求必须提供 caller_user_id。
    返回规范化后的 user_id。
    """
    if not getattr(settings, "strict_user_isolation", False):
        return _norm(caller_user_id) if caller_user_id is not None else ""
    if caller_user_id is None or not str(caller_user_id).strip():
        raise HTTPException(
            status_code=400,
            detail=f"strict_user_isolation=true 时必须在查询参数中提供 user_id 以访问 {resource}。",
        )
    return _norm(caller_user_id)


def assert_trace_access(rec: TraceRecord, caller_user_id: str | None) -> None:
    """校验 Trace 归属。严格模式必须传 user_id；非严格模式传了则校验。"""
    owner = _norm(rec.request.user_id)
    if getattr(settings, "strict_user_isolation", False):
        cid = require_user_id_for_strict_mode(caller_user_id, resource="trace")
        if cid != owner:
            raise HTTPException(status_code=403, detail="无权访问该 trace（user_id 不匹配）。")
        return
    if caller_user_id is None or not str(caller_user_id).strip():
        return
    if _norm(caller_user_id) != owner:
        raise HTTPException(status_code=403, detail="无权访问该 trace（user_id 不匹配）。")


def assert_ltm_access(item: LTMItem, caller_user_id: str | None) -> None:
    """校验 LTM 条目归属。"""
    owner = _norm(item.user_id)
    if getattr(settings, "strict_user_isolation", False):
        cid = require_user_id_for_strict_mode(caller_user_id, resource="LTM")
        if cid != owner:
            raise HTTPException(status_code=403, detail="无权操作该记忆（user_id 不匹配）。")
        return
    if caller_user_id is None or not str(caller_user_id).strip():
        return
    if _norm(caller_user_id) != owner:
        raise HTTPException(status_code=403, detail="无权操作该记忆（user_id 不匹配）。")


def assert_profile_access(owner_user_id: str, viewer_user_id: str | None) -> None:
    """查看画像：strict 或传入 viewer 时，查看者须与 owner 一致。"""
    owner = _norm(owner_user_id)
    if getattr(settings, "strict_user_isolation", False):
        vid = require_user_id_for_strict_mode(viewer_user_id, resource="profile")
        if vid != owner:
            raise HTTPException(status_code=403, detail="无权查看该用户画像（user_id 不匹配）。")
        return
    if viewer_user_id is None or not str(viewer_user_id).strip():
        return
    if _norm(viewer_user_id) != owner:
        raise HTTPException(status_code=403, detail="无权查看该用户画像（user_id 不匹配）。")
