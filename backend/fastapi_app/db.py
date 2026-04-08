"""Shared psycopg access for Django-free FastAPI code paths."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import settings

_pool: ConnectionPool | None = None


def _build_conninfo() -> str:
    conninfo_kwargs: dict[str, Any] = {
        "dbname": settings.db_name,
        "user": settings.db_user,
        "password": settings.db_password,
        "host": settings.db_host,
        "port": settings.db_port,
        "connect_timeout": settings.db_connect_timeout,
        "options": f"-c search_path={settings.db_search_path}",
    }
    if settings.db_sslmode:
        conninfo_kwargs["sslmode"] = settings.db_sslmode

    filtered_kwargs = {
        key: value for key, value in conninfo_kwargs.items() if value not in (None, "")
    }
    return make_conninfo(**filtered_kwargs)


def get_pool() -> ConnectionPool:
    global _pool
    if _pool is None:
        _pool = ConnectionPool(
            conninfo=_build_conninfo(),
            kwargs={
                "autocommit": True,
                "row_factory": dict_row,
            },
            min_size=settings.db_pool_min_size,
            max_size=settings.db_pool_max_size,
            timeout=settings.db_pool_timeout,
            max_waiting=settings.db_pool_max_waiting,
            open=True,
        )
    return _pool


def fetch_all(sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    with get_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            return list(cursor.fetchall())


def fetch_one(sql: str, params: Mapping[str, Any] | None = None) -> dict[str, Any] | None:
    with get_pool().connection() as connection:
        with connection.cursor() as cursor:
            cursor.execute(sql, params or {})
            return cursor.fetchone()


def fetch_scalar(sql: str, params: Mapping[str, Any] | None = None) -> Any:
    row = fetch_one(sql, params)
    if row is None:
        return None
    return next(iter(row.values()))
