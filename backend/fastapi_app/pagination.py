"""Pagination helpers matching the current Django API envelope."""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

from fastapi import Request

from .config import settings


@dataclass(frozen=True)
class PageWindow:
    page: int
    page_size: int
    offset: int
    limit: int


def _parse_positive_int(raw_value: str | None, default: int) -> int:
    if raw_value is None:
        return default

    try:
        value = int(raw_value)
    except (TypeError, ValueError):
        return default

    return value if value > 0 else default


def get_page_window(request: Request) -> PageWindow:
    page = _parse_positive_int(request.query_params.get("page"), 1)
    requested_page_size = _parse_positive_int(
        request.query_params.get("page_size"),
        settings.default_page_size,
    )
    page_size = min(requested_page_size, settings.max_page_size)
    offset = (page - 1) * page_size
    return PageWindow(page=page, page_size=page_size, offset=offset, limit=page_size)


def build_bundle_envelope(
    request: Request,
    route_name: str,
    resources: list[dict],
    total_count: int,
    page: int,
    page_size: int,
) -> dict:
    def canonicalize_resource_url(url: str) -> str:
        parts = urlsplit(url)
        path = parts.path.rstrip("/") or "/"
        return urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))

    entries = [
        {
            "fullUrl": canonicalize_resource_url(str(request.url_for(route_name, id=resource["id"]))),
            "resource": resource,
        }
        for resource in resources
    ]

    page_count = (total_count + page_size - 1) // page_size if total_count else 0

    next_url = None
    if total_count and page < page_count:
        next_url = str(request.url.include_query_params(page=page + 1, page_size=page_size))

    previous_url = None
    if page > 1:
        previous_url = str(request.url.include_query_params(page=page - 1, page_size=page_size))

    return {
        "count": total_count,
        "next": next_url,
        "previous": previous_url,
        "results": {
            "resourceType": "Bundle",
            "type": "searchset",
            "total": len(entries),
            "entry": entries,
        },
    }
