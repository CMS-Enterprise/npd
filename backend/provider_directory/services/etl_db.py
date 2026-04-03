"""Shared psycopg access for provider-directory reads against the ETL CoreDM DB."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from psycopg.conninfo import make_conninfo
from psycopg.rows import dict_row
from psycopg_pool import ConnectionPool

_DEFAULT_ETL_SEARCH_PATH = "core_data_model,public"


@dataclass(frozen=True)
class ETLSettings:
    db_host: str | None = os.getenv("NPD_ETL_DB_HOST", "127.0.0.1")
    db_name: str | None = os.getenv("NPD_ETL_DB_NAME", "myapp_dev")
    db_user: str | None = os.getenv("NPD_ETL_DB_USER", "devuser")
    db_password: str | None = os.getenv("NPD_ETL_DB_PASSWORD", "simple")
    db_port: str | None = os.getenv("NPD_ETL_DB_PORT", "5432")
    db_sslmode: str | None = os.getenv("NPD_ETL_DB_SSLMODE")
    db_gssencmode: str | None = os.getenv("NPD_ETL_DB_GSSENCMODE", "disable")
    db_connect_timeout: int = int(os.getenv("NPD_ETL_DB_CONNECT_TIMEOUT", "10"))
    db_search_path: str = os.getenv("NPD_ETL_DB_SEARCH_PATH", _DEFAULT_ETL_SEARCH_PATH)
    db_pool_min_size: int = int(os.getenv("NPD_ETL_DB_POOL_MIN_SIZE", "1"))
    db_pool_max_size: int = int(os.getenv("NPD_ETL_DB_POOL_MAX_SIZE", "10"))
    db_pool_timeout: int = int(os.getenv("NPD_ETL_DB_POOL_TIMEOUT", "10"))
    db_pool_max_waiting: int = int(os.getenv("NPD_ETL_DB_POOL_MAX_WAITING", "10"))


settings = ETLSettings()
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
        "gssencmode": settings.db_gssencmode,
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
