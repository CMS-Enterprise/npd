"""Django-free Location query helpers using psycopg and direct SQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping

from fhir.resources.R4B.location import Location as FHIRLocation, LocationPosition
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar
from .organization_native_service import _organization_reference
from .practitioner_native_service import ADDRESS_USE_TO_NPD, _build_address, _build_phone, _parse_identifier_query


@dataclass(frozen=True)
class LocationListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class LocationSearchParams:
    name: str | None
    organization_name: str | None
    organization_identifier: str | None
    organization_type: str | None
    address: str | None
    address_city: str | None
    address_state: str | None
    address_postalcode: str | None
    address_use: str | None
    near: str | None
    sort: str | None


@dataclass(frozen=True)
class SqlFilter:
    where_sql: str
    params: dict[str, Any]


_LOCATION_BASE_FROM = """
FROM location l
JOIN organization o ON o.id = l.organization_id
LEFT JOIN organization_view ov ON ov.id = l.organization_id
LEFT JOIN address a ON a.id = l.address_id
LEFT JOIN address_us au ON au.id = a.address_us_id
"""

_LOCATION_BASE_SELECT = """
SELECT
    l.id,
    l.name,
    l.organization_id,
    l.address_id,
    l.active,
    l.phone_id,
    ov.name AS organization_name,
    au.latitude,
    au.longitude
"""


def _build_count_from(search_params: LocationSearchParams) -> str:
    joins: list[str] = ["FROM location l"]

    needs_address_join = any(
        (
            search_params.address,
            search_params.address_city,
            search_params.address_state,
            search_params.address_postalcode,
            search_params.near,
        )
    )
    if needs_address_join:
        joins.extend(
            [
                "LEFT JOIN address a ON a.id = l.address_id",
                "LEFT JOIN address_us au ON au.id = a.address_us_id",
            ]
        )

    return "\n".join(joins)


def _endpoint_reference(base_url: str, endpoint_instance_id: Any) -> dict[str, Any]:
    return Reference(reference=f"{base_url.rstrip('/')}/fhir/Endpoint/{endpoint_instance_id}").model_dump()


def _parse_search_params(query_params: Mapping[str, str]) -> LocationSearchParams:
    return LocationSearchParams(
        name=query_params.get("name"),
        organization_name=query_params.get("organization_name"),
        organization_identifier=query_params.get("organization_identifier"),
        organization_type=query_params.get("organization_type"),
        address=query_params.get("address"),
        address_city=query_params.get("address_city"),
        address_state=query_params.get("address_state"),
        address_postalcode=query_params.get("address_postalcode"),
        address_use=query_params.get("address_use"),
        near=query_params.get("near"),
        sort=query_params.get("_sort"),
    )


def _build_filters(search_params: LocationSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.name:
        clauses.append("l.name LIKE %(name_like)s")
        params["name_like"] = f"%{search_params.name}%"

    if search_params.organization_name:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_name otn
                WHERE otn.organization_id = l.organization_id
                  AND otn.search_vector @@ websearch_to_tsquery('english', %(organization_name_query)s)
            )
            """
        )
        params["organization_name_query"] = search_params.organization_name.upper()

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
                        WHERE co.organization_id = l.organization_id
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
                        WHERE co.organization_id = l.organization_id
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
                    WHERE co.organization_id = l.organization_id
                      AND otoi.other_id = %(organization_identifier_other_id)s
                )
                """
            )
            params["organization_identifier_other_id"] = identifier_value

            clauses.append("(" + " OR ".join(identifier_clauses) + ")")

    if search_params.organization_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM clinical_organization co
                JOIN organization_to_taxonomy ott ON ott.npi = co.npi
                WHERE co.organization_id = l.organization_id
                  AND to_tsvector('english', ott.nucc_code) @@ websearch_to_tsquery('english', %(organization_type_query)s)
            )
            """
        )
        params["organization_type_query"] = search_params.organization_type

    if search_params.address:
        clauses.append("au.search_vector @@ websearch_to_tsquery('english', %(address_query)s)")
        params["address_query"] = search_params.address

    if search_params.address_city:
        clauses.append("au.city_name = %(address_city)s")
        params["address_city"] = search_params.address_city

    if search_params.address_state:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM fips_state fs
                WHERE fs.id = au.state_code
                  AND fs.abbreviation = %(address_state)s
            )
            """
        )
        params["address_state"] = search_params.address_state

    if search_params.address_postalcode:
        clauses.append("au.zipcode = %(address_postalcode)s")
        params["address_postalcode"] = search_params.address_postalcode

    if search_params.address_use:
        address_use_id = ADDRESS_USE_TO_NPD.get(search_params.address_use)
        if address_use_id is None:
            clauses.append("FALSE")
        else:
            clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM organization_to_address ota
                    WHERE ota.organization_id = l.organization_id
                      AND ota.address_id = l.address_id
                      AND ota.address_use_id = %(address_use_id)s
                )
                """
            )
            params["address_use_id"] = address_use_id

    if search_params.near:
        clauses.append(
            """
            ST_DWithin(
                au.geolocation::geography,
                ST_SetSRID(ST_MakePoint(%(near_lon)s, %(near_lat)s), 4326)::geography,
                %(near_distance_meters)s
            )
            """
        )
        raw_parts = search_params.near.split("|")
        if len(raw_parts) < 3:
            clauses[-1] = "FALSE"
        else:
            lat = float(raw_parts[0])
            lon = float(raw_parts[1])
            distance = float(raw_parts[2])
            units = raw_parts[3] if len(raw_parts) > 3 else "km"
            multiplier = {"km": 1000.0, "mi": 1609.344, "ft": 0.3048}.get(units, 1000.0)
            params["near_lat"] = lat
            params["near_lon"] = lon
            params["near_distance_meters"] = distance * multiplier

    if not clauses:
        return SqlFilter(where_sql="", params=params)
    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "name": "l.name",
        "organization_name": "organization_name",
    }

    if not sort_param:
        return "ORDER BY l.name"

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
        return "ORDER BY l.name"
    return "ORDER BY " + ", ".join(fields)


def _fetch_location_address_rows(location_ids: list[Any]) -> dict[Any, dict[str, Any] | None]:
    if not location_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            l.id AS location_id,
            ota.address_id,
            ota.address_use_id,
            fau.value AS address_use_value,
            au.delivery_line_1,
            au.delivery_line_2,
            au.city_name,
            fs.abbreviation AS state_abbreviation,
            au.zipcode,
            au.latitude,
            au.longitude
        FROM location l
        LEFT JOIN organization_to_address ota
            ON ota.organization_id = l.organization_id
           AND ota.address_id = l.address_id
        LEFT JOIN fhir_address_use fau ON fau.id = ota.address_use_id
        LEFT JOIN address a ON a.id = l.address_id
        LEFT JOIN address_us au ON au.id = a.address_us_id
        LEFT JOIN fips_state fs ON fs.id = au.state_code
        WHERE l.id = ANY(%(location_ids)s::uuid[])
        ORDER BY l.id, ota.address_use_id, ota.address_id
        """,
        {"location_ids": location_ids},
    )
    grouped: dict[Any, dict[str, Any] | None] = {}
    for row in rows:
        grouped.setdefault(row["location_id"], row)
    return grouped


def _fetch_location_phone_rows(phone_ids: list[Any]) -> dict[Any, dict[str, Any]]:
    if not phone_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            otp.id,
            otp.phone_number,
            otp.extension,
            otp.phone_use_id,
            fpu.value AS phone_use_value
        FROM organization_to_phone otp
        JOIN fhir_phone_use fpu ON fpu.id = otp.phone_use_id
        WHERE otp.id = ANY(%(phone_ids)s::uuid[])
        """,
        {"phone_ids": phone_ids},
    )
    return {row["id"]: row for row in rows}


def _fetch_location_endpoint_rows(location_ids: list[Any]) -> dict[Any, list[Any]]:
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
    grouped: dict[Any, list[Any]] = defaultdict(list)
    for row in rows:
        grouped[row["location_id"]].append(row["endpoint_instance_id"])
    return grouped


def _build_location_resource(
    base_row: Mapping[str, Any],
    *,
    base_url: str,
    address_row: Mapping[str, Any] | None,
    phone_row: Mapping[str, Any] | None,
    endpoint_ids: list[Any],
) -> dict[str, Any]:
    location = FHIRLocation()
    location.id = str(base_row["id"])
    location.status = "active" if base_row["active"] else "inactive"
    location.name = base_row["name"]

    if phone_row is not None:
        location.telecom = [_build_phone(phone_row)]

    if address_row is not None and address_row["delivery_line_1"] is not None:
        location.address = _build_address(address_row)
        if address_row["longitude"] is not None and address_row["latitude"] is not None:
            location.position = LocationPosition(
                latitude=address_row["latitude"],
                longitude=address_row["longitude"],
            )

    location.managingOrganization = _organization_reference(base_url, base_row["organization_id"])

    if endpoint_ids:
        location.endpoint = [_endpoint_reference(base_url, endpoint_id) for endpoint_id in endpoint_ids]

    return location.model_dump()


def _load_location_resources(base_rows: list[dict[str, Any]], *, base_url: str) -> list[dict[str, Any]]:
    location_ids = [row["id"] for row in base_rows]
    phone_ids = [row["phone_id"] for row in base_rows if row["phone_id"] is not None]

    address_rows = _fetch_location_address_rows(location_ids)
    phone_rows = _fetch_location_phone_rows(phone_ids)
    endpoint_rows = _fetch_location_endpoint_rows(location_ids)

    resources: list[dict[str, Any]] = []
    for base_row in base_rows:
        resources.append(
            _build_location_resource(
                base_row,
                base_url=base_url,
                address_row=address_rows.get(base_row["id"]),
                phone_row=phone_rows.get(base_row["phone_id"]),
                endpoint_ids=endpoint_rows.get(base_row["id"], []),
            )
        )
    return resources


def list_location_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> LocationListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    count_from_sql = _build_count_from(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {count_from_sql}
        {sql_filter.where_sql}
        """,
        sql_params,
    )
    if total_count is None:
        total_count = 0

    sql_params.update({"limit": page_size, "offset": (page - 1) * page_size})
    base_rows = fetch_all(
        f"""
        {_LOCATION_BASE_SELECT}
        {_LOCATION_BASE_FROM}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s
        OFFSET %(offset)s
        """,
        sql_params,
    )
    resources = _load_location_resources(base_rows, base_url=base_url)
    return LocationListResult(resources=resources, total_count=int(total_count))


def get_location_resource(location_id: str, *, base_url: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_LOCATION_BASE_SELECT}
        {_LOCATION_BASE_FROM}
        WHERE l.id = %(location_id)s::uuid
        LIMIT 1
        """,
        {"location_id": location_id},
    )
    if base_row is None:
        return None
    return _load_location_resources([base_row], base_url=base_url)[0]
