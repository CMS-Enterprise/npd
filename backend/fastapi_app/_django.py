"""Helpers for bootstrapping Django inside the FastAPI process."""

from __future__ import annotations

from dataclasses import dataclass
import os
import threading

_SETUP_LOCK = threading.Lock()
_SETUP_COMPLETE = False


def ensure_django() -> None:
    """Initialize Django exactly once for ORM/filter/serializer reuse."""
    global _SETUP_COMPLETE

    if _SETUP_COMPLETE:
        return

    with _SETUP_LOCK:
        if _SETUP_COMPLETE:
            return

        os.environ.setdefault("DJANGO_SETTINGS_MODULE", "app.settings")

        import django

        django.setup()
        _SETUP_COMPLETE = True


@dataclass(frozen=True)
class DjangoRequestAdapter:
    """Minimal adapter for serializers that expect Django request helpers."""

    base_url: str

    def build_absolute_uri(self, path: str) -> str:
        if path.startswith(("http://", "https://")):
            return path

        normalized_base = self.base_url.rstrip("/")
        normalized_path = path if path.startswith("/") else f"/{path}"
        return f"{normalized_base}{normalized_path}"
