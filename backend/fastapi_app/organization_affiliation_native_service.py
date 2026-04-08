"""Django-free OrganizationAffiliation query helpers using psycopg and direct SQL."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.organizationaffiliation import (
    OrganizationAffiliation as FHIROrganizationAffiliation,
)
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar
from .practitioner_native_service import _parse_identifier_query


@dataclass(frozen=True)
class OrganizationAffiliationListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class OrganizationAffiliationSearchParams:
    primary_organization_name: str | None
    participating_organization_name: str | None
    participating_organization_identifier: str | None
    participating_organization_type: str | None
    location_address: str | None
    location_address_city: str | None
    location_address_state: str | None
    location_address_postalcode: str | None
    sort: str | None


@dataclass(frozen=True)
class SqlFilter:
    where_sql: str
    params: dict[str, Any]


_ORGANIZATION_AFFILIATION_BASE_FROM = """
FROM organization_affiliation oa
"""

_ORGANIZATION_AFFILIATION_BASE_SELECT = """
SELECT
    oa.id,
    oa.organization_id,
    oa.ehr_vendor_id,
    oa.organization_name,
    oa.ehr_vendor_name,
    oa.npi,
    oa.location_ids,
    oa.endpoint_instance_ids,
    oa.taxonomy_codes
"""


def _parse_search_params(query_params: Mapping[str, str]) -> OrganizationAffiliationSearchParams:
    return OrganizationAffiliationSearchParams(
        primary_organization_name=query_params.get("primary_organization_name"),
        participating_organization_name=query_params.get("participating_organization_name"),
        participating_organization_identifier=query_params.get("participating_organization_identifier"),
        participating_organization_type=query_params.get("participating_organization_type"),
        location_address=query_params.get("location_address"),
        location_address_city=query_params.get("location_address_city"),
        location_address_state=query_params.get("location_address_state"),
        location_address_postalcode=query_params.get("location_address_postalcode"),
        sort=query_params.get("_sort"),
    )


def _build_filters(search_params: OrganizationAffiliationSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.primary_organization_name:
        clauses.append(
            """
            to_tsvector('english', oa.ehr_vendor_name) @@ websearch_to_tsquery(
                'english',
                %(primary_organization_name_query)s
            )
            """
        )
        params["primary_organization_name_query"] = search_params.primary_organization_name

    if search_params.participating_organization_name:
        clauses.append("oa.organization_name ILIKE %(participating_organization_name_like)s")
        params["participating_organization_name_like"] = (
            f"%{search_params.participating_organization_name}%"
        )

    if search_params.participating_organization_identifier:
        system, identifier_value = _parse_identifier_query(
            search_params.participating_organization_identifier
        )
        try:
            npi_value = int(identifier_value)
        except (TypeError, ValueError):
            npi_value = None

        if npi_value is None:
            clauses.append("FALSE")
        elif system is None or system.upper() == "NPI":
            clauses.append("oa.npi = %(participating_organization_npi)s")
            params["participating_organization_npi"] = npi_value
        else:
            clauses.append("FALSE")

    if search_params.participating_organization_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM nucc nu
                WHERE nu.display_name ILIKE %(participating_organization_type_like)s
                  AND oa.taxonomy_codes && ARRAY[nu.code]::varchar[]
            )
            """
        )
        params["participating_organization_type_like"] = (
            f"%{search_params.participating_organization_type}%"
        )

    if search_params.location_address:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM unnest(oa.location_ids) AS loc_id
                JOIN location l ON l.id = loc_id
                JOIN address a ON a.id = l.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE au.search_vector @@ websearch_to_tsquery('english', %(location_address_query)s)
            )
            """
        )
        params["location_address_query"] = search_params.location_address

    if search_params.location_address_city:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM unnest(oa.location_ids) AS loc_id
                JOIN location l ON l.id = loc_id
                JOIN address a ON a.id = l.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE au.city_name = %(location_address_city)s
            )
            """
        )
        params["location_address_city"] = search_params.location_address_city

    if search_params.location_address_state:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM unnest(oa.location_ids) AS loc_id
                JOIN location l ON l.id = loc_id
                JOIN address a ON a.id = l.address_id
                JOIN address_us au ON au.id = a.address_us_id
                JOIN fips_state fs ON fs.id = au.state_code
                WHERE fs.abbreviation = %(location_address_state)s
            )
            """
        )
        params["location_address_state"] = search_params.location_address_state

    if search_params.location_address_postalcode:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM unnest(oa.location_ids) AS loc_id
                JOIN location l ON l.id = loc_id
                JOIN address a ON a.id = l.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE au.zipcode = %(location_address_postalcode)s
            )
            """
        )
        params["location_address_postalcode"] = search_params.location_address_postalcode

    if not clauses:
        return SqlFilter(where_sql="", params=params)
    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "ehr_vendor_name": "oa.ehr_vendor_name",
        "organization_name": "oa.organization_name",
    }

    if not sort_param:
        return "ORDER BY oa.organization_name"

    fields: list[str] = []
    for raw_field in sort_param.split(","):
        raw_field = raw_field.strip()
        if not raw_field:
            continue
        descending = raw_field.startswith("-")
        field_name = raw_field[1:] if descending else raw_field
        resolved_field = ordering_map.get(field_name)
        if resolved_field is None:
            continue
        fields.append(f"{resolved_field} DESC" if descending else resolved_field)

    if not fields:
        return "ORDER BY oa.organization_name"
    return "ORDER BY " + ", ".join(fields)


def _organization_reference(display: str) -> dict[str, Any]:
    return Reference(display=str(display)).model_dump()


def _participating_organization_reference(
    base_url: str,
    organization_id: Any,
    display: str,
) -> dict[str, Any]:
    reference = Reference(reference=f"{base_url.rstrip('/')}/fhir/Organization/{organization_id}")
    reference.display = str(display)
    return reference.model_dump()


def _location_reference(base_url: str, location_id: Any) -> dict[str, Any]:
    return Reference(reference=f"{base_url.rstrip('/')}/fhir/Location/{location_id}").model_dump()


def _endpoint_reference(base_url: str, endpoint_id: Any) -> dict[str, Any]:
    return Reference(reference=f"{base_url.rstrip('/')}/fhir/Endpoint/{endpoint_id}").model_dump()


def _build_organization_affiliation_resource(
    base_row: Mapping[str, Any],
    *,
    base_url: str,
) -> dict[str, Any]:
    organization_affiliation = FHIROrganizationAffiliation()
    organization_affiliation.id = str(base_row["id"])
    organization_affiliation.organization = _organization_reference(base_row["ehr_vendor_name"])
    organization_affiliation.participatingOrganization = _participating_organization_reference(
        base_url,
        base_row["organization_id"],
        base_row["organization_name"],
    )
    organization_affiliation.code = [
        CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/codesystem-organization-role",
                    code="HIE/HIO",
                    display="HIE/HIO",
                )
            ]
        )
    ]
    organization_affiliation.location = [
        _location_reference(base_url, location_id) for location_id in (base_row["location_ids"] or [])
    ]
    organization_affiliation.endpoint = [
        _endpoint_reference(base_url, endpoint_id)
        for endpoint_id in (base_row["endpoint_instance_ids"] or [])
    ]
    return organization_affiliation.model_dump()


def list_organization_affiliation_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> OrganizationAffiliationListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {_ORGANIZATION_AFFILIATION_BASE_FROM}
        {sql_filter.where_sql}
        """,
        sql_params,
    )
    if total_count is None:
        total_count = 0

    sql_params.update({"limit": page_size, "offset": (page - 1) * page_size})
    base_rows = fetch_all(
        f"""
        {_ORGANIZATION_AFFILIATION_BASE_SELECT}
        {_ORGANIZATION_AFFILIATION_BASE_FROM}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        sql_params,
    )
    return OrganizationAffiliationListResult(
        resources=[
            _build_organization_affiliation_resource(row, base_url=base_url) for row in base_rows
        ],
        total_count=int(total_count),
    )


def get_organization_affiliation_resource(affiliation_id: str, *, base_url: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_ORGANIZATION_AFFILIATION_BASE_SELECT}
        {_ORGANIZATION_AFFILIATION_BASE_FROM}
        WHERE oa.id = %(affiliation_id)s::uuid
        """,
        {"affiliation_id": affiliation_id},
    )
    if base_row is None:
        return None

    return _build_organization_affiliation_resource(base_row, base_url=base_url)
