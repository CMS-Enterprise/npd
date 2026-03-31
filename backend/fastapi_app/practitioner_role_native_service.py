"""Django-free PractitionerRole query helpers using psycopg and direct SQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.practitionerrole import PractitionerRole
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar
from .practitioner_native_service import GENDER_TO_NPD, _parse_identifier_query


@dataclass(frozen=True)
class PractitionerRoleListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class PractitionerRoleSearchParams:
    practitioner_name: str | None
    practitioner_gender: str | None
    practitioner_type: str | None
    practitioner_identifier: str | None
    organization_name: str | None
    organization_type: str | None
    organization_identifier: str | None
    location_near: str | None
    location_address: str | None
    location_address_city: str | None
    location_address_state: str | None
    location_address_postalcode: str | None
    active: str | None
    role: str | None
    specialty: str | None
    endpoint_connection_type: str | None
    endpoint_payload_type: str | None
    endpoint_status: str | None
    sort: str | None


@dataclass(frozen=True)
class SqlFilter:
    where_sql: str
    params: dict[str, Any]


_PRACTITIONER_ROLE_BASE_FROM = """
FROM provider_to_location_view ptlv
JOIN provider_to_organization pto ON pto.id = ptlv.provider_to_organization_id
LEFT JOIN location l ON l.id = ptlv.location_id
LEFT JOIN address a ON a.id = l.address_id
LEFT JOIN address_us au ON au.id = a.address_us_id
"""

_PRACTITIONER_ROLE_BASE_SELECT = """
SELECT
    ptlv.id,
    ptlv.active,
    ptlv.specialty_id,
    ptlv.provider_role_code,
    ptlv.location_id,
    ptlv.location_name,
    ptlv.practitioner_first_name,
    ptlv.practitioner_last_name,
    ptlv.organization_name,
    pto.individual_id,
    pto.organization_id
"""


def _parse_search_params(query_params: Mapping[str, str]) -> PractitionerRoleSearchParams:
    return PractitionerRoleSearchParams(
        practitioner_name=query_params.get("practitioner_name"),
        practitioner_gender=query_params.get("practitioner_gender"),
        practitioner_type=query_params.get("practitioner_type"),
        practitioner_identifier=query_params.get("practitioner_identifier"),
        organization_name=query_params.get("organization_name"),
        organization_type=query_params.get("organization_type"),
        organization_identifier=query_params.get("organization_identifier"),
        location_near=query_params.get("location_near"),
        location_address=query_params.get("location_address"),
        location_address_city=query_params.get("location_address_city"),
        location_address_state=query_params.get("location_address_state"),
        location_address_postalcode=query_params.get("location_address_postalcode"),
        active=query_params.get("active"),
        role=query_params.get("role"),
        specialty=query_params.get("specialty"),
        endpoint_connection_type=query_params.get("endpoint_connection_type"),
        endpoint_payload_type=query_params.get("endpoint_payload_type"),
        endpoint_status=query_params.get("endpoint_status"),
        sort=query_params.get("_sort"),
    )


def _parse_bool(value: str | None) -> bool | None:
    if value is None:
        return None
    normalized = value.strip().lower()
    if normalized in {"1", "true", "t", "yes"}:
        return True
    if normalized in {"0", "false", "f", "no"}:
        return False
    return None


def _build_filters(search_params: PractitionerRoleSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.practitioner_name:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM individual_to_name itn
                WHERE itn.individual_id = pto.individual_id
                  AND itn.search_vector @@ websearch_to_tsquery('english', %(practitioner_name_query)s)
            )
            """
        )
        params["practitioner_name_query"] = search_params.practitioner_name

    if search_params.practitioner_gender:
        gender_value = GENDER_TO_NPD.get(search_params.practitioner_gender)
        if gender_value is None:
            clauses.append("FALSE")
        else:
            clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM individual i
                    WHERE i.id = pto.individual_id
                      AND i.gender = %(practitioner_gender)s
                )
                """
            )
            params["practitioner_gender"] = gender_value

    if search_params.practitioner_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM provider p
                JOIN provider_to_taxonomy ptt ON ptt.npi = p.npi
                JOIN nucc nu ON nu.code = ptt.nucc_code
                WHERE p.individual_id = pto.individual_id
                  AND nu.search_vector @@ websearch_to_tsquery('english', %(practitioner_type_query)s)
            )
            """
        )
        params["practitioner_type_query"] = search_params.practitioner_type

    if search_params.practitioner_identifier:
        system, identifier_value = _parse_identifier_query(search_params.practitioner_identifier)
        npi_value: int | None = None
        try:
            npi_value = int(identifier_value)
        except (TypeError, ValueError):
            npi_value = None

        if system is not None:
            if system.upper() == "NPI" and npi_value is not None:
                clauses.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM provider p
                        WHERE p.individual_id = pto.individual_id
                          AND p.npi = %(practitioner_identifier_npi)s
                    )
                    """
                )
                params["practitioner_identifier_npi"] = npi_value
            else:
                clauses.append("FALSE")
        else:
            identifier_clauses: list[str] = []
            if npi_value is not None:
                identifier_clauses.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM provider p
                        WHERE p.individual_id = pto.individual_id
                          AND p.npi = %(practitioner_identifier_npi)s
                    )
                    """
                )
                params["practitioner_identifier_npi"] = npi_value

            identifier_clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM provider p
                    JOIN provider_to_other_id ptoi ON ptoi.npi = p.npi
                    WHERE p.individual_id = pto.individual_id
                      AND ptoi.other_id = %(practitioner_identifier_other_id)s
                )
                """
            )
            params["practitioner_identifier_other_id"] = identifier_value
            clauses.append("(" + " OR ".join(identifier_clauses) + ")")

    if search_params.organization_name:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_name otn
                WHERE otn.organization_id = pto.organization_id
                  AND otn.search_vector @@ websearch_to_tsquery('english', %(organization_name_query)s)
            )
            """
        )
        params["organization_name_query"] = search_params.organization_name.upper()

    if search_params.organization_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM clinical_organization co
                JOIN organization_to_taxonomy ott ON ott.npi = co.npi
                JOIN nucc nu ON nu.code = ott.nucc_code
                WHERE co.organization_id = pto.organization_id
                  AND nu.search_vector @@ websearch_to_tsquery('english', %(organization_type_query)s)
            )
            """
        )
        params["organization_type_query"] = search_params.organization_type

    if search_params.organization_identifier:
        system, identifier_value = _parse_identifier_query(search_params.organization_identifier)
        npi_value: int | None = None
        try:
            npi_value = int(identifier_value)
        except (TypeError, ValueError):
            npi_value = None

        if system is not None:
            if system.upper() == "NPI" and npi_value is not None:
                clauses.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM clinical_organization co
                        WHERE co.organization_id = pto.organization_id
                          AND co.npi = %(organization_identifier_npi)s
                    )
                    """
                )
                params["organization_identifier_npi"] = npi_value
            else:
                clauses.append("FALSE")
        else:
            identifier_clauses: list[str] = []
            if npi_value is not None:
                identifier_clauses.append(
                    """
                    EXISTS (
                        SELECT 1
                        FROM clinical_organization co
                        WHERE co.organization_id = pto.organization_id
                          AND co.npi = %(organization_identifier_npi)s
                    )
                    """
                )
                params["organization_identifier_npi"] = npi_value

            identifier_clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM clinical_organization co
                    JOIN organization_to_other_id otoi ON otoi.npi = co.npi
                    WHERE co.organization_id = pto.organization_id
                      AND otoi.other_id = %(organization_identifier_other_id)s
                )
                """
            )
            params["organization_identifier_other_id"] = identifier_value
            clauses.append("(" + " OR ".join(identifier_clauses) + ")")

    if search_params.location_near:
        raw_parts = search_params.location_near.split("|")
        if len(raw_parts) < 3:
            clauses.append("FALSE")
        else:
            lat = float(raw_parts[0])
            lon = float(raw_parts[1])
            distance = float(raw_parts[2])
            units = raw_parts[3] if len(raw_parts) > 3 else "km"
            multiplier = {"km": 1000.0, "mi": 1609.344, "ft": 0.3048}.get(units, 1000.0)
            clauses.append(
                """
                ST_DWithin(
                    au.geolocation::geography,
                    ST_SetSRID(ST_MakePoint(%(location_near_lon)s, %(location_near_lat)s), 4326)::geography,
                    %(location_near_distance_meters)s
                )
                """
            )
            params["location_near_lat"] = lat
            params["location_near_lon"] = lon
            params["location_near_distance_meters"] = distance * multiplier

    if search_params.location_address:
        clauses.append("au.search_vector @@ websearch_to_tsquery('english', %(location_address_query)s)")
        params["location_address_query"] = search_params.location_address

    if search_params.location_address_city:
        clauses.append("au.city_name = %(location_address_city)s")
        params["location_address_city"] = search_params.location_address_city

    if search_params.location_address_state:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM fips_state fs
                WHERE fs.id = au.state_code
                  AND fs.abbreviation = %(location_address_state)s
            )
            """
        )
        params["location_address_state"] = search_params.location_address_state

    if search_params.location_address_postalcode:
        clauses.append("au.zipcode = %(location_address_postalcode)s")
        params["location_address_postalcode"] = search_params.location_address_postalcode

    if search_params.active is not None:
        active_value = _parse_bool(search_params.active)
        if active_value is None:
            clauses.append("FALSE")
        else:
            clauses.append("ptlv.active = %(active)s")
            params["active"] = active_value

    if search_params.role:
        clauses.append("ptlv.provider_role_code ILIKE %(role)s")
        params["role"] = search_params.role

    if search_params.specialty:
        clauses.append("ptlv.specialty_id::text ILIKE %(specialty)s")
        params["specialty"] = search_params.specialty

    if search_params.endpoint_connection_type:
        clauses.append("ei_filter.endpoint_connection_type_id = %(endpoint_connection_type)s")
        params["endpoint_connection_type"] = search_params.endpoint_connection_type

    if search_params.endpoint_payload_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM location_to_endpoint_instance ltei
                JOIN endpoint_instance_to_payload eitp ON eitp.endpoint_instance_id = ltei.endpoint_instance_id
                WHERE ltei.location_id = ptlv.location_id
                  AND eitp.payload_type_id = %(endpoint_payload_type)s
            )
            """
        )
        params["endpoint_payload_type"] = search_params.endpoint_payload_type

    if search_params.endpoint_status:
        clauses.append("ei_filter.status = %(endpoint_status)s")
        params["endpoint_status"] = search_params.endpoint_status

    if not clauses:
        return SqlFilter(where_sql="", params=params)
    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_extra_joins(search_params: PractitionerRoleSearchParams) -> str:
    if search_params.endpoint_connection_type or search_params.endpoint_status:
        return """
JOIN location_to_endpoint_instance ltei_filter ON ltei_filter.location_id = ptlv.location_id
JOIN endpoint_instance ei_filter ON ei_filter.id = ltei_filter.endpoint_instance_id
"""
    return ""


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "location_name": "ptlv.location_name",
        "practitioner_first_name": "ptlv.practitioner_first_name",
        "practitioner_last_name": "ptlv.practitioner_last_name",
        "organization_name": "ptlv.organization_name",
    }

    if not sort_param:
        return "ORDER BY ptlv.location_name"

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
        return "ORDER BY ptlv.location_name"
    return "ORDER BY " + ", ".join(fields)


def _practitioner_reference(base_url: str, practitioner_id: Any, display: str | None = None) -> dict[str, Any]:
    reference = Reference(reference=f"{base_url.rstrip('/')}/fhir/Practitioner/{practitioner_id}")
    if display:
        reference.display = display
    return reference.model_dump()


def _organization_reference(base_url: str, organization_id: Any, display: str | None = None) -> dict[str, Any]:
    reference = Reference(reference=f"{base_url.rstrip('/')}/fhir/Organization/{organization_id}")
    if display:
        reference.display = display
    return reference.model_dump()


def _location_reference(base_url: str, location_id: Any) -> dict[str, Any]:
    return Reference(reference=f"{base_url.rstrip('/')}/fhir/Location/{location_id}").model_dump()


def _endpoint_reference(base_url: str, endpoint_id: Any) -> dict[str, Any]:
    return Reference(reference=f"{base_url.rstrip('/')}/fhir/Endpoint/{endpoint_id}").model_dump()


def _fetch_location_endpoint_rows(location_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not location_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            location_id,
            endpoint_instance_id
        FROM location_to_endpoint_instance
        WHERE location_id = ANY(%(location_ids)s::uuid[])
        ORDER BY location_id, endpoint_instance_id
        """,
        {"location_ids": location_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["location_id"]].append(row)
    return grouped


def _build_practitioner_role_resource(
    base_row: Mapping[str, Any],
    *,
    endpoint_rows: list[Mapping[str, Any]],
    base_url: str,
) -> dict[str, Any]:
    practitioner_display = " ".join(
        part
        for part in [base_row["practitioner_first_name"], base_row["practitioner_last_name"]]
        if part
    )
    role_kwargs: dict[str, Any] = {
        "id": str(base_row["id"]),
        "active": base_row["active"],
        "practitioner": _practitioner_reference(
            base_url,
            base_row["individual_id"],
            practitioner_display or None,
        ),
        "organization": _organization_reference(
            base_url,
            base_row["organization_id"],
            base_row["organization_name"],
        ),
        "location": [_location_reference(base_url, base_row["location_id"])],
    }

    if base_row["specialty_id"] is not None:
        role_kwargs["specialty"] = (
            CodeableConcept(
                coding=[
                    Coding(
                        system="http://snomed.info/sct",
                        code=str(base_row["specialty_id"]),
                    )
                ]
            ),
        )

    if endpoint_rows:
        role_kwargs["endpoint"] = [
            _endpoint_reference(base_url, row["endpoint_instance_id"]) for row in endpoint_rows
        ]

    return PractitionerRole(**role_kwargs).model_dump()


def _load_practitioner_role_resources(
    base_rows: list[dict[str, Any]],
    *,
    base_url: str,
) -> list[dict[str, Any]]:
    location_ids = [row["location_id"] for row in base_rows]
    endpoint_rows = _fetch_location_endpoint_rows(location_ids)

    resources: list[dict[str, Any]] = []
    for base_row in base_rows:
        resources.append(
            _build_practitioner_role_resource(
                base_row,
                endpoint_rows=endpoint_rows.get(base_row["location_id"], []),
                base_url=base_url,
            )
        )
    return resources


def list_practitioner_role_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> PractitionerRoleListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    extra_joins = _build_extra_joins(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {_PRACTITIONER_ROLE_BASE_FROM}
        {extra_joins}
        {sql_filter.where_sql}
        """,
        sql_params,
    )
    if total_count is None:
        total_count = 0

    sql_params.update({"limit": page_size, "offset": (page - 1) * page_size})
    base_rows = fetch_all(
        f"""
        {_PRACTITIONER_ROLE_BASE_SELECT}
        {_PRACTITIONER_ROLE_BASE_FROM}
        {extra_joins}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s OFFSET %(offset)s
        """,
        sql_params,
    )
    return PractitionerRoleListResult(
        resources=_load_practitioner_role_resources(base_rows, base_url=base_url),
        total_count=int(total_count),
    )


def get_practitioner_role_resource(role_id: str, *, base_url: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_PRACTITIONER_ROLE_BASE_SELECT}
        {_PRACTITIONER_ROLE_BASE_FROM}
        WHERE ptlv.id = %(role_id)s::uuid
        """,
        {"role_id": role_id},
    )
    if base_row is None:
        return None

    return _load_practitioner_role_resources([base_row], base_url=base_url)[0]
