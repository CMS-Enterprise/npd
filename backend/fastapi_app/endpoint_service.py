"""Endpoint query helpers for the FastAPI experiment server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ._django import ensure_django


@dataclass(frozen=True)
class EndpointListResult:
    resources: list[dict]
    total_count: int


def _build_filter_querydict(query_params: Mapping[str, str]):
    ensure_django()

    from django.http import QueryDict

    querydict = QueryDict("", mutable=True)
    for key, value in query_params.items():
        querydict.appendlist(key, value)
    return querydict


def _get_base_queryset():
    ensure_django()

    from django.db.models import F

    from npdfhir.models import EndpointInstance

    return (
        EndpointInstance.objects.all()
        .prefetch_related(
            "endpoint_connection_type",
            "environment_type",
            "endpointinstancetopayload_set",
            "endpointinstancetopayload_set__payload_type",
            "endpointinstancetopayload_set__mime_type",
            "endpointinstancetootherid_set",
        )
        .annotate(ehr_vendor_name=F("ehr_vendor__name"))
    )


def _apply_filters(queryset, query_params: Mapping[str, str]):
    ensure_django()

    from npdfhir.filters.endpoint_filter_set import EndpointFilterSet

    filterset = EndpointFilterSet(
        data=_build_filter_querydict(query_params),
        queryset=queryset,
    )
    return filterset.qs


def _apply_ordering(queryset, sort_param: str | None):
    ordering_map = {
        "name": "name",
        "address": "address",
        "ehr_vendor_name": "ehr_vendor_name",
    }

    if not sort_param:
        return queryset.order_by("name")

    fields = []
    for raw_field in sort_param.split(","):
        raw_field = raw_field.strip()
        if not raw_field:
            continue

        descending = raw_field.startswith("-")
        field_name = raw_field[1:] if descending else raw_field
        resolved_field = ordering_map.get(field_name)
        if not resolved_field:
            continue

        fields.append(f"-{resolved_field}" if descending else resolved_field)

    if not fields:
        fields = ["name"]

    return queryset.order_by(*fields)


def list_endpoint_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
) -> EndpointListResult:
    ensure_django()

    from npdfhir.serializers import EndpointSerializer

    queryset = _get_base_queryset()
    queryset = _apply_filters(queryset, query_params)
    queryset = _apply_ordering(queryset, query_params.get("_sort"))

    total_count = queryset.count()
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    resources = EndpointSerializer(rows, many=True).data

    return EndpointListResult(resources=list(resources), total_count=total_count)


def get_endpoint_resource(endpoint_id: str) -> dict | None:
    ensure_django()

    from npdfhir.serializers import EndpointSerializer

    queryset = _get_base_queryset()
    endpoint = queryset.filter(id=endpoint_id).first()
    if endpoint is None:
        return None

    return EndpointSerializer(endpoint).data
