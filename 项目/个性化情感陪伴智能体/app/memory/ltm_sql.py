"""LTM 的 SQL 实现（与 InMemoryLTMStore 相同接口；MySQL 等通过 DATABASE_URL）。"""

from __future__ import annotations

import json
import threading
import uuid
from collections.abc import Iterator
from typing import Any

from sqlalchemy import BigInteger, Boolean, Float, String, Text, and_, create_engine, func, select
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, sessionmaker

from app.memory.ltm import LTMItem, LTMType


class Base(DeclarativeBase):
    pass


class LTMRow(Base):
    __tablename__ = "ltm_items"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    user_id: Mapped[str] = mapped_column(String(128), index=True, nullable=False)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    # 毫秒时间戳，超出 MySQL INT；须 BIGINT
    created_at: Mapped[int] = mapped_column(BigInteger, nullable=False)
    source: Mapped[str] = mapped_column(String(512), default="")
    confidence: Mapped[float] = mapped_column(Float, default=1.0)
    tags_json: Mapped[str] = mapped_column(Text, default="[]")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[int] = mapped_column(BigInteger, default=0)
    embedding_status: Mapped[str] = mapped_column(String(16), default="pending")


_engine: Any = None
_SessionLocal: sessionmaker[Session] | None = None
_init_lock = threading.Lock()


def _connect_timeout_args(database_url: str) -> dict:
    """缩短首次建连等待，避免 /health 与启动路径在不可达库上挂死整进程事件循环。"""
    u = database_url.lower()
    if "+pymysql" in u or "mysql" in u:
        return {"connect_timeout": 3}
    if "postgresql" in u:
        return {"connect_timeout": 3}
    return {}


def _ensure_engine(database_url: str) -> None:
    global _engine, _SessionLocal
    with _init_lock:
        if _engine is not None:
            return
        ca = _connect_timeout_args(database_url)
        eng = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            connect_args=ca,
        )
        try:
            Base.metadata.create_all(eng)
        except Exception:
            eng.dispose()
            raise
        _SessionLocal = sessionmaker(bind=eng, autoflush=False, autocommit=False)
        _engine = eng


def init_ltm_db(database_url: str) -> None:
    """应用启动时可显式调用：建表（若不存在）。"""
    _ensure_engine(database_url)


def ping_database(database_url: str) -> None:
    """探活：SELECT 1（供 /health 使用）。"""
    _ensure_engine(database_url)
    from sqlalchemy import text

    assert _engine is not None
    with _engine.connect() as c:
        c.execute(text("SELECT 1"))


def _row_to_item(row: LTMRow) -> LTMItem:
    try:
        tags = json.loads(row.tags_json or "[]")
        if not isinstance(tags, list):
            tags = []
    except (json.JSONDecodeError, TypeError):
        tags = []
    t: LTMType = row.type if row.type in ("Preference", "Profile", "Event", "Constraint") else "Event"
    es = row.embedding_status if row.embedding_status in ("pending", "ready", "failed") else "pending"
    return LTMItem(
        id=row.id,
        user_id=row.user_id,
        type=t,
        content=row.content,
        created_at=row.created_at,
        source=row.source or "",
        confidence=float(row.confidence),
        tags=[str(x) for x in tags],
        is_active=bool(row.is_active),
        updated_at=int(row.updated_at or 0),
        embedding_status=es,
    )


class SQLLTMStore:
    def __init__(self, database_url: str) -> None:
        _ensure_engine(database_url)
        self._lock = threading.Lock()

    def _session(self) -> Session:
        assert _SessionLocal is not None
        return _SessionLocal()

    def put(self, user_id: str, item: LTMItem) -> str:
        now = item.created_at
        if item.updated_at <= 0:
            item = item.model_copy(update={"updated_at": now})
        uid = (item.id or "").strip()
        if not uid:
            uid = str(uuid.uuid4())
            item = item.model_copy(update={"id": uid, "user_id": user_id})
        else:
            item = item.model_copy(update={"user_id": user_id})
        tags_json = json.dumps(item.tags, ensure_ascii=False)
        with self._lock:
            with self._session() as s:
                row = s.get(LTMRow, uid)
                if row is None:
                    row = LTMRow(id=uid)
                    s.add(row)
                row.user_id = user_id
                row.type = item.type
                row.content = item.content
                row.created_at = item.created_at
                row.source = item.source or ""
                row.confidence = float(item.confidence)
                row.tags_json = tags_json
                row.is_active = bool(item.is_active)
                row.updated_at = int(item.updated_at)
                row.embedding_status = item.embedding_status
                s.commit()
        return uid

    def update_item(
        self,
        *,
        id: str,
        content: str | None = None,
        tags: list[str] | None = None,
        confidence: float | None = None,
        is_active: bool | None = None,
        updated_at: int | None = None,
    ) -> LTMItem | None:
        with self._lock:
            with self._session() as s:
                cur = s.get(LTMRow, id)
                if cur is None:
                    return None
                item = _row_to_item(cur)
                update: dict[str, Any] = {}
                if content is not None:
                    update["content"] = content
                if tags is not None:
                    update["tags"] = tags
                if confidence is not None:
                    update["confidence"] = confidence
                if is_active is not None:
                    update["is_active"] = is_active
                update["updated_at"] = int(updated_at or item.updated_at or item.created_at)
                nxt = item.model_copy(update=update)
                cur.content = nxt.content
                cur.confidence = float(nxt.confidence)
                cur.tags_json = json.dumps(nxt.tags, ensure_ascii=False)
                cur.is_active = bool(nxt.is_active)
                cur.updated_at = int(nxt.updated_at)
                s.commit()
                s.refresh(cur)
                return _row_to_item(cur)

    def soft_delete(self, *, id: str, updated_at: int | None = None) -> LTMItem | None:
        return self.update_item(id=id, is_active=False, updated_at=updated_at)

    def get_by_id(self, id: str) -> LTMItem | None:
        with self._lock:
            with self._session() as s:
                row = s.get(LTMRow, id)
                if row is None:
                    return None
                return _row_to_item(row)

    def list_by_user(
        self,
        user_id: str,
        type: LTMType | None = None,
        limit: int = 20,
        offset: int = 0,
        q: str | None = None,
        only_active: bool = True,
        source: str | None = None,
    ) -> tuple[list[LTMItem], int]:
        q_norm = (q or "").strip().lower()
        src_norm = (source or "").strip()
        off = max(0, int(offset))
        lim = max(1, int(limit))
        conds: list[Any] = [LTMRow.user_id == user_id]
        if only_active:
            conds.append(LTMRow.is_active.is_(True))
        if type is not None:
            conds.append(LTMRow.type == type)
        if src_norm:
            conds.append(LTMRow.source == src_norm)
        # 与 InMemory「子串包含」一致；避免 LIKE 把用户输入中的 % _ 当通配符
        if q_norm:
            conds.append(func.instr(func.lower(LTMRow.content), q_norm) > 0)
        where_clause = and_(*conds)

        with self._lock:
            with self._session() as s:
                total = int(s.scalar(select(func.count()).select_from(LTMRow).where(where_clause)) or 0)
                page_stmt = (
                    select(LTMRow)
                    .where(where_clause)
                    .order_by(LTMRow.created_at.desc(), LTMRow.id.desc())
                    .limit(lim)
                    .offset(off)
                )
                rows = list(s.scalars(page_stmt).all())
                return [_row_to_item(r) for r in rows], total

    def iter_active_ltm_items(self) -> Iterator[LTMItem]:
        """供 RAG 启动预热：全表 is_active 条目（不在持锁期间 yield）。"""
        with self._lock:
            with self._session() as s:
                rows = list(s.scalars(select(LTMRow).where(LTMRow.is_active.is_(True))).all())
        for row in rows:
            yield _row_to_item(row)
