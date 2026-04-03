"""Organization query helpers for the FastAPI experiment server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ._django import DjangoRequestAdapter, ensure_django


@dataclass(frozen=True)
class OrganizationListResult:
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

    from npdfhir.models import OrganizationView

    return OrganizationView.objects.prefetch_related(
        "authorized_official",
        "ein",
        "organization",
        "organization__organizationtoname_set",
        "organization__organizationtoaddress_set",
        "organization__organizationtoaddress_set__address",
        "organization__organizationtoaddress_set__address__address_us",
        "organization__organizationtoaddress_set__address__address_us__state_code",
        "organization__organizationtoaddress_set__address_use",
        "organization__authorized_official__individualtophone_set",
        "organization__authorized_official__individualtoname_set",
        "organization__authorized_official__individualtoemail_set",
        "organization__authorized_official__individualtoaddress_set",
        "organization__authorized_official__individualtoaddress_set__address__address_us",
        "organization__authorized_official__individualtoaddress_set__address__address_us__state_code",
        "organization__clinicalorganization",
        "organization__clinicalorganization__npi",
        "organization__clinicalorganization__organizationtootherid_set",
        "organization__clinicalorganization__organizationtootherid_set__other_id_type",
        "organization__clinicalorganization__organizationtotaxonomy_set",
        "organization__clinicalorganization__organizationtotaxonomy_set__nucc_code",
    )


def _apply_filters(queryset, query_params: Mapping[str, str]):
    ensure_django()

    from npdfhir.filters.organization_filter_set import OrganizationFilterSet

    filterset = OrganizationFilterSet(
        data=_build_filter_querydict(query_params),
        queryset=queryset,
    )
    return filterset.qs


def _apply_ordering(queryset, sort_param: str | None):
    ordering_map = {
        "name": "name",
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


def list_organization_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> OrganizationListResult:
    ensure_django()

    from npdfhir.serializers import OrganizationSerializer

    queryset = _get_base_queryset()
    queryset = _apply_filters(queryset, query_params)
    queryset = _apply_ordering(queryset, query_params.get("_sort"))

    total_count = queryset.count()
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    resources = OrganizationSerializer(
        rows,
        many=True,
        context=_serializer_context(base_url),
    ).data

    return OrganizationListResult(resources=list(resources), total_count=total_count)


def get_organization_resource(organization_id: str, *, base_url: str) -> dict | None:
    ensure_django()

    from npdfhir.serializers import OrganizationSerializer

    queryset = _get_base_queryset()
    organization = queryset.filter(organization_id=organization_id).first()
    if organization is None:
        return None

    return OrganizationSerializer(
        organization,
        context=_serializer_context(base_url),
    ).data
