"""OrganizationAffiliation query helpers for the FastAPI experiment server."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from ._django import DjangoRequestAdapter, ensure_django


@dataclass(frozen=True)
class OrganizationAffiliationListResult:
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

    from npdfhir.models import OrganizationAffiliationView

    return OrganizationAffiliationView.objects.all().select_related(
        "organization",
        "ehr_vendor",
    )


def _apply_filters(queryset, query_params: Mapping[str, str]):
    ensure_django()

    from npdfhir.filters.organization_affiliation_filter_set import (
        OrganizationAffiliationFilterSet,
    )

    filterset = OrganizationAffiliationFilterSet(
        data=_build_filter_querydict(query_params),
        queryset=queryset,
    )
    return filterset.qs


def _apply_ordering(queryset, sort_param: str | None):
    ordering_map = {
        "ehr_vendor_name": "ehr_vendor_name",
        "organization_name": "organization_name",
    }

    if not sort_param:
        return queryset.order_by("organization_name")

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
        fields = ["organization_name"]

    return queryset.order_by(*fields)


def _serializer_context(base_url: str) -> dict[str, DjangoRequestAdapter]:
    return {"request": DjangoRequestAdapter(base_url=base_url)}


def list_organization_affiliation_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> OrganizationAffiliationListResult:
    ensure_django()

    from npdfhir.serializers import OrganizationAffiliationSerializer

    queryset = _get_base_queryset()
    queryset = _apply_filters(queryset, query_params)
    queryset = _apply_ordering(queryset, query_params.get("_sort"))

    total_count = queryset.count()
    offset = (page - 1) * page_size
    rows = list(queryset[offset : offset + page_size])
    resources = OrganizationAffiliationSerializer(
        rows,
        many=True,
        context=_serializer_context(base_url),
    ).data

    return OrganizationAffiliationListResult(resources=list(resources), total_count=total_count)


def get_organization_affiliation_resource(affiliation_id: str, *, base_url: str) -> dict | None:
    ensure_django()

    from npdfhir.serializers import OrganizationAffiliationSerializer

    queryset = _get_base_queryset()
    affiliation = queryset.filter(pk=affiliation_id).first()
    if affiliation is None:
        return None

    return OrganizationAffiliationSerializer(
        affiliation,
        context=_serializer_context(base_url),
    ).data
