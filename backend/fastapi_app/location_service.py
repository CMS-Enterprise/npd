"""Location query helpers for the FastAPI experiment server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ._django import DjangoRequestAdapter, ensure_django


@dataclass(frozen=True)
class LocationListResult:
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

    from django.db.models import F, Prefetch

    from npdfhir.models import Location, OrganizationToAddress

    return (
        Location.objects.all()
        .select_related(
            "organization",
            "address",
            "address__address_us",
            "address__address_us__state_code",
        )
        .prefetch_related(
            Prefetch(
                "organization__organizationtoaddress_set",
                queryset=OrganizationToAddress.objects.select_related(
                    "address_use", "address__address_us", "address__address_us__state_code"
                ),
            ),
            "locationtoendpointinstance_set",
        )
        .annotate(
            organization_name=F("organization__organizationtoname__name"),
        )
    )


def _apply_filters(queryset, query_params: Mapping[str, str]):
    ensure_django()

    from npdfhir.filters.location_filter_set import LocationFilterSet

    filterset = LocationFilterSet(
        data=_build_filter_querydict(query_params),
        queryset=queryset,
    )
    return filterset.qs


def _apply_ordering(queryset, sort_param: str | None):
    ordering_map = {
        "name": "name",
        "organization_name": "organization_name",
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


def _serializer_context(base_url: str) -> dict[str, DjangoRequestAdapter]:
    return {"request": DjangoRequestAdapter(base_url=base_url)}


def list_location_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> LocationListResult:
    ensure_django()

    from npdfhir.serializers import LocationSerializer

    queryset = _get_base_queryset()
    queryset = _apply_filters(queryset, query_params)
    queryset = _apply_ordering(queryset, query_params.get("_sort"))

    total_count = queryset.count()
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    resources = LocationSerializer(
        rows,
        many=True,
        context=_serializer_context(base_url),
    ).data

    return LocationListResult(resources=list(resources), total_count=total_count)


def get_location_resource(location_id: str, *, base_url: str) -> dict | None:
    ensure_django()

    from npdfhir.serializers import LocationSerializer

    queryset = _get_base_queryset()
    location = queryset.filter(id=location_id).first()
    if location is None:
        return None

    return LocationSerializer(
        location,
        context=_serializer_context(base_url),
    ).data
