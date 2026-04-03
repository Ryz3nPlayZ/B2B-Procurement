from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

from backend.db.database import get_conn


def utc_now() -> str:
    return datetime.utcnow().isoformat() + "Z"


def make_id(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:12]}"


def fetch_one(query: str, params: tuple[Any, ...]) -> dict | None:
    with get_conn() as conn:
        row = conn.execute(query, params).fetchone()
    return dict(row) if row else None


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict]:
    with get_conn() as conn:
        rows = conn.execute(query, params).fetchall()
    return [dict(r) for r in rows]


def execute(query: str, params: tuple[Any, ...]) -> None:
    with get_conn() as conn:
        conn.execute(query, params)


def executemany(query: str, params: list[tuple[Any, ...]]) -> None:
    with get_conn() as conn:
        conn.executemany(query, params)
