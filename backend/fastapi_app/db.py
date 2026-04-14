"""Shared psycopg access for Django-free FastAPI code paths."""

from __future__ import annotations

import logging
from collections.abc import Mapping
from typing import Any, Callable

import psycopg
from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

from .config import settings

_pool: ConnectionPool | None = None
logger = logging.getLogger(__name__)


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


def reset_pool() -> None:
    global _pool
    if _pool is not None:
        _pool.close()
        _pool = None


def _is_retryable_connection_error(exc: BaseException) -> bool:
    message = str(exc).lower()
    return any(
        token in message
        for token in (
            "ssl syscall error: eof detected",
            "consuming input failed",
            "server closed the connection unexpectedly",
            "connection not open",
            "closed the connection",
        )
    )


def _execute_with_retry(
    sql: str,
    params: Mapping[str, Any] | None,
    fetch: Callable[[Any], Any],
) -> Any:
    for attempt in range(2):
        try:
            with get_pool().connection() as connection:
                with connection.cursor() as cursor:
                    cursor.execute(sql, params or {})
                    return fetch(cursor)
        except (psycopg.OperationalError, psycopg.InterfaceError) as exc:
            if attempt == 0 and _is_retryable_connection_error(exc):
                logger.warning("Retrying DB query after connection error: %s", exc)
                reset_pool()
                continue
            raise


def fetch_all(sql: str, params: Mapping[str, Any] | None = None) -> list[dict[str, Any]]:
    return _execute_with_retry(sql, params, lambda cursor: list(cursor.fetchall()))


def fetch_one(sql: str, params: Mapping[str, Any] | None = None) -> dict[str, Any] | None:
    return _execute_with_retry(sql, params, lambda cursor: cursor.fetchone())


def fetch_scalar(sql: str, params: Mapping[str, Any] | None = None) -> Any:
    row = fetch_one(sql, params)
    if row is None:
        return None
    return next(iter(row.values()))
