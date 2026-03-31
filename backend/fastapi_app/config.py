"""Runtime settings for the experimental FastAPI server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Final


@dataclass(frozen=True)
class Settings:
    app_name: str = "NPD FastAPI Experiment"
    app_version: str = "0.1.0"
    default_page_size: int = int(os.getenv("FASTAPI_DEFAULT_PAGE_SIZE", "10"))
    max_page_size: int = int(os.getenv("FASTAPI_MAX_PAGE_SIZE", "1000"))
    db_host: str | None = os.getenv("NPD_DB_HOST")
    db_name: str | None = os.getenv("NPD_DB_NAME")
    db_user: str | None = os.getenv("NPD_DB_USER")
    db_password: str | None = os.getenv("NPD_DB_PASSWORD")
    db_port: str | None = os.getenv("NPD_DB_PORT")
    db_sslmode: str | None = os.getenv("NPD_DB_SSLMODE")
    db_connect_timeout: int = int(os.getenv("FASTAPI_DB_CONNECT_TIMEOUT", "10"))
    db_search_path: Final[str] = "npd,public"
    db_pool_min_size: int = int(os.getenv("FASTAPI_DB_POOL_MIN_SIZE", "1"))
    db_pool_max_size: int = int(os.getenv("FASTAPI_DB_POOL_MAX_SIZE", "10"))
    db_pool_timeout: int = int(os.getenv("FASTAPI_DB_POOL_TIMEOUT", "10"))
    db_pool_max_waiting: int = int(os.getenv("FASTAPI_DB_POOL_MAX_WAITING", "10"))


settings = Settings()
