"""Normalization helpers for Django-vs-FastAPI response comparison."""

from __future__ import annotations

import json
from urllib.parse import parse_qsl, urlsplit, urlunsplit
from typing import Any


IGNORED_HEADERS = {
    "date",
    "server",
    "content-length",
    "vary",
    "x-frame-options",
    "referrer-policy",
    "cross-origin-opener-policy",
    "set-cookie",
    "djdt-store-id",
    "server-timing",
}


def normalize_headers(headers: dict[str, str]) -> dict[str, str]:
    return {
        key.lower(): value
        for key, value in headers.items()
        if key.lower() not in IGNORED_HEADERS
    }


def _normalize_url(value: str, local_netlocs: set[str], *, strip_local_trailing_slash: bool) -> str:
    parts = urlsplit(value)
    if not parts.scheme or not parts.netloc:
        return value
    if parts.netloc not in local_netlocs:
        return value

    normalized_query = "&".join(
        f"{key}={query_value}" for key, query_value in sorted(parse_qsl(parts.query, keep_blank_values=True))
    )
    normalized_path = (parts.path.rstrip("/") or "/") if strip_local_trailing_slash else (parts.path or "/")
    return urlunsplit(("http", "__BASE__", normalized_path, normalized_query, ""))


def _normalize_json(value: Any, local_netlocs: set[str], *, strip_local_trailing_slash: bool) -> Any:
    if isinstance(value, dict):
        normalized = {
            key: _normalize_json(
                item,
                local_netlocs,
                strip_local_trailing_slash=strip_local_trailing_slash,
            )
            for key, item in value.items()
        }
        if normalized.get("resourceType") == "CapabilityStatement" and "date" in normalized:
            normalized["date"] = "__DATETIME__"
        return normalized
    if isinstance(value, list):
        return [
            _normalize_json(
                item,
                local_netlocs,
                strip_local_trailing_slash=strip_local_trailing_slash,
            )
            for item in value
        ]
    if isinstance(value, str):
        return _normalize_url(
            value,
            local_netlocs,
            strip_local_trailing_slash=strip_local_trailing_slash,
        )
    return value


def normalize_body(
    content_type: str | None,
    body: str,
    *,
    local_netlocs: set[str] | None = None,
    strip_local_trailing_slash: bool = True,
) -> Any:
    if content_type and "json" in content_type:
        return _normalize_json(
            json.loads(body),
            local_netlocs or set(),
            strip_local_trailing_slash=strip_local_trailing_slash,
        )
    return body
