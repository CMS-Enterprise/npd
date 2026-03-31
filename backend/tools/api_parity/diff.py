"""Diff helpers for parity reporting."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ComparisonResult:
    classification: str
    status_match: bool
    content_type_match: bool
    body_match: bool


def classify_response_pair(
    *,
    django_status: int,
    fastapi_status: int,
    django_content_type: str | None,
    fastapi_content_type: str | None,
    django_body: Any,
    fastapi_body: Any,
) -> ComparisonResult:
    status_match = django_status == fastapi_status
    content_type_match = django_content_type == fastapi_content_type
    body_match = django_body == fastapi_body

    classification = (
        "exact_match" if status_match and content_type_match and body_match else "contract_mismatch"
    )

    return ComparisonResult(
        classification=classification,
        status_match=status_match,
        content_type_match=content_type_match,
        body_match=body_match,
    )

