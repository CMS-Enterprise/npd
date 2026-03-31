"""Django-free Endpoint query helpers using psycopg and direct SQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.endpoint import Endpoint
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar


@dataclass(frozen=True)
class EndpointListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class EndpointSearchParams:
    name: str | None
    connection_type: str | None
    payload_type: str | None
    status: str | None
    sort: str | None


@dataclass(frozen=True)
class SqlFilter:
    where_sql: str
    params: dict[str, Any]


_ENDPOINT_BASE_FROM = """
FROM endpoint_instance ei
LEFT JOIN endpoint_connection_type ect ON ect.id = ei.endpoint_connection_type_id
LEFT JOIN ehr_vendor ev ON ev.id = ei.ehr_vendor_id
"""

_ENDPOINT_BASE_SELECT = """
SELECT
    ei.id,
    ei.ehr_vendor_id,
    ei.address,
    ei.endpoint_connection_type_id,
    ei.name,
    ei.description,
    ei.environment_type_id,
    ei.status,
    ect.display AS endpoint_connection_type_display,
    ev.name AS ehr_vendor_name
"""


def _parse_search_params(query_params: Mapping[str, str]) -> EndpointSearchParams:
    return EndpointSearchParams(
        name=query_params.get("name"),
        connection_type=query_params.get("connection_type"),
        payload_type=query_params.get("payload_type"),
        status=query_params.get("status"),
        sort=query_params.get("_sort"),
    )


def _build_filters(search_params: EndpointSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.name:
        clauses.append("ei.name ILIKE %(name_like)s")
        params["name_like"] = f"%{search_params.name}%"

    if search_params.connection_type:
        clauses.append("ei.endpoint_connection_type_id ILIKE %(connection_type_like)s")
        params["connection_type_like"] = f"%{search_params.connection_type}%"

    if search_params.payload_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM endpoint_instance_to_payload eitp
                WHERE eitp.endpoint_instance_id = ei.id
                  AND eitp.payload_type_id ILIKE %(payload_type_like)s
            )
            """
        )
        params["payload_type_like"] = f"%{search_params.payload_type}%"

    if not clauses:
        return SqlFilter(where_sql="", params=params)
    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "name": "ei.name",
        "address": "ei.address",
        "ehr_vendor_name": "ehr_vendor_name",
    }

    if not sort_param:
        return "ORDER BY ei.name"

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
        return "ORDER BY ei.name"
    return "ORDER BY " + ", ".join(fields)


def _fetch_endpoint_identifier_rows(endpoint_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not endpoint_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            endpoint_instance_id,
            other_id,
            system,
            issuer_id
        FROM endpoint_instance_to_other_id
        WHERE endpoint_instance_id = ANY(%(endpoint_ids)s::uuid[])
        ORDER BY endpoint_instance_id, other_id, system, issuer_id
        """,
        {"endpoint_ids": endpoint_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["endpoint_instance_id"]].append(row)
    return grouped


def _fetch_endpoint_payload_rows(endpoint_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not endpoint_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            eitp.endpoint_instance_id,
            eitp.payload_type_id,
            pt.value AS payload_type_value
        FROM endpoint_instance_to_payload eitp
        JOIN payload_type pt ON pt.id = eitp.payload_type_id
        WHERE eitp.endpoint_instance_id = ANY(%(endpoint_ids)s::uuid[])
        ORDER BY eitp.endpoint_instance_id, eitp.payload_type_id
        """,
        {"endpoint_ids": endpoint_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["endpoint_instance_id"]].append(row)
    return grouped


def _build_endpoint_identifier(row: Mapping[str, Any]) -> dict[str, Any]:
    return Identifier(
        use="official",
        system=row["system"],
        value=row["other_id"],
        assigner=Reference(display=str(row["issuer_id"])),
    ).model_dump()


def _build_payload_type(row: Mapping[str, Any]) -> dict[str, Any]:
    return CodeableConcept(
        coding=[
            Coding(
                system="http://terminology.hl7.org/CodeSystem/endpoint-payload-type",
                code=row["payload_type_id"],
                display=row["payload_type_value"],
            )
        ]
    ).model_dump()


def _build_endpoint_resource(
    base_row: Mapping[str, Any],
    *,
    identifier_rows: list[Mapping[str, Any]],
    payload_rows: list[Mapping[str, Any]],
) -> dict[str, Any]:
    endpoint_kwargs: dict[str, Any] = {
        "id": str(base_row["id"]),
        "identifier": [_build_endpoint_identifier(row) for row in identifier_rows],
        "status": "active",
        "name": base_row["name"],
        "payloadType": [_build_payload_type(row) for row in payload_rows],
        "address": base_row["address"],
    }

    if base_row["endpoint_connection_type_id"]:
        endpoint_kwargs["connectionType"] = Coding(
            system="http://terminology.hl7.org/CodeSystem/endpoint-connection-type",
            code=base_row["endpoint_connection_type_id"],
            display=base_row["endpoint_connection_type_display"],
        )

    return Endpoint(**endpoint_kwargs).model_dump()


def _load_endpoint_resources(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    endpoint_ids = [row["id"] for row in base_rows]
    identifier_rows = _fetch_endpoint_identifier_rows(endpoint_ids)
    payload_rows = _fetch_endpoint_payload_rows(endpoint_ids)

    resources: list[dict[str, Any]] = []
    for base_row in base_rows:
        resources.append(
            _build_endpoint_resource(
                base_row,
                identifier_rows=identifier_rows.get(base_row["id"], []),
                payload_rows=payload_rows.get(base_row["id"], []),
            )
        )
    return resources


def list_endpoint_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
) -> EndpointListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {_ENDPOINT_BASE_FROM}
        {sql_filter.where_sql}
        """,
        sql_params,
    )
    if total_count is None:
        total_count = 0

    sql_params.update({"limit": page_size, "offset": (page - 1) * page_size})
    base_rows = fetch_all(
        f"""
        {_ENDPOINT_BASE_SELECT}
        {_ENDPOINT_BASE_FROM}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s
        OFFSET %(offset)s
        """,
        sql_params,
    )
    resources = _load_endpoint_resources(base_rows)
    return EndpointListResult(resources=resources, total_count=int(total_count))


def get_endpoint_resource(endpoint_id: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_ENDPOINT_BASE_SELECT}
        {_ENDPOINT_BASE_FROM}
        WHERE ei.id = %(endpoint_id)s::uuid
        LIMIT 1
        """,
        {"endpoint_id": endpoint_id},
    )
    if base_row is None:
        return None
    return _load_endpoint_resources([base_row])[0]
