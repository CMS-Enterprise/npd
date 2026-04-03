"""Practitioner query helpers for the FastAPI experiment server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ._django import ensure_django


@dataclass(frozen=True)
class PractitionerListResult:
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

    from django.db.models import Prefetch

    from npdfhir.models import IndividualToAddress, ProviderView

    return ProviderView.objects.all().prefetch_related(
        "provider__individual",
        "provider__npi",
        "provider",
        Prefetch(
            "provider__individual__individualtoaddress_set",
            queryset=IndividualToAddress.objects.select_related(
                "address_use",
                "address__address_us",
                "address__address_us__state_code",
            ),
        ),
        "provider__individual__individualtophone_set",
        "provider__individual__individualtoemail_set",
        "provider__individual__individualtoname_set",
        "provider__providertootherid_set",
        "provider__providertootherid_set__other_id_type",
        "provider__providertootherid_set__state_code",
        "provider__providertotaxonomy_set",
        "provider__providertotaxonomy_set__nucc_code",
    )


def _apply_filters(queryset, query_params: Mapping[str, str]):
    ensure_django()

    from npdfhir.filters.practitioner_filter_set import PractitionerFilterSet

    filterset = PractitionerFilterSet(
        data=_build_filter_querydict(query_params),
        queryset=queryset,
    )
    return filterset.qs


def _apply_ordering(queryset, sort_param: str | None):
    ordering_map = {
        "last_name": "last_name",
        "first_name": "first_name",
        "npi_value": "npi__npi",
    }

    if not sort_param:
        return queryset.order_by("last_name", "first_name")

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
        fields = ["last_name", "first_name"]

    return queryset.order_by(*fields)


def list_practitioner_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
) -> PractitionerListResult:
    ensure_django()

    from npdfhir.serializers import PractitionerSerializer

    queryset = _get_base_queryset()
    queryset = _apply_filters(queryset, query_params)
    queryset = _apply_ordering(queryset, query_params.get("_sort"))

    total_count = queryset.count()
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    resources = PractitionerSerializer(rows, many=True).data

    return PractitionerListResult(resources=list(resources), total_count=total_count)


def get_practitioner_resource(practitioner_id: str) -> dict | None:
    ensure_django()

    from npdfhir.serializers import PractitionerSerializer

    queryset = _get_base_queryset()
    provider = queryset.filter(provider_id=practitioner_id).first()
    if provider is None:
        return None

    return PractitionerSerializer(provider).data

