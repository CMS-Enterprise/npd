"""Runtime settings for the experimental FastAPI server."""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = "NPD FastAPI Experiment"
    app_version: str = "0.1.0"
    default_page_size: int = int(os.getenv("FASTAPI_DEFAULT_PAGE_SIZE", "10"))
    max_page_size: int = int(os.getenv("FASTAPI_MAX_PAGE_SIZE", "1000"))


settings = Settings()

