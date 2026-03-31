"""Django-free Organization query helpers using psycopg and direct SQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping
from uuid import UUID

from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.extension import Extension
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.organization import Organization as FHIROrganization
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar
from .practitioner_native_service import (
    ADDRESS_USE_TO_NPD,
    _build_address,
    _build_email,
    _build_name,
    _build_npi_identifier,
    _build_other_identifier,
    _build_phone,
    _fetch_related_emails,
    _fetch_related_names,
    _fetch_related_phones,
    _parse_identifier_query,
)


ORGANIZATION_PROFILE_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-organization"


@dataclass(frozen=True)
class OrganizationListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class OrganizationSearchParams:
    name: str | None
    identifier: str | None
    organization_type: str | None
    address: str | None
    address_city: str | None
    address_state: str | None
    address_postalcode: str | None
    address_use: str | None
    sort: str | None


@dataclass(frozen=True)
class SqlFilter:
    where_sql: str
    params: dict[str, Any]


_ORGANIZATION_BASE_FROM = """
FROM organization_view ov
JOIN organization o ON o.id = ov.id
LEFT JOIN legal_entity le ON le.ein_id = ov.ein_id
"""

_ORGANIZATION_BASE_SELECT = """
SELECT
    ov.id AS organization_id,
    ov.authorized_official_id,
    ov.ein_id,
    ov.parent_id,
    ov.name AS sort_name
"""


def _organization_reference(base_url: str, organization_id: Any, display: str | None = None) -> dict[str, Any]:
    reference = Reference(reference=f"{base_url.rstrip('/')}/fhir/Organization/{organization_id}")
    if display:
        reference.display = display
    return reference.model_dump()


def _parse_search_params(query_params: Mapping[str, str]) -> OrganizationSearchParams:
    return OrganizationSearchParams(
        name=query_params.get("name"),
        identifier=query_params.get("identifier"),
        organization_type=query_params.get("organization_type"),
        address=query_params.get("address"),
        address_city=query_params.get("address_city"),
        address_state=query_params.get("address_state"),
        address_postalcode=query_params.get("address_postalcode"),
        address_use=query_params.get("address_use"),
        sort=query_params.get("_sort"),
    )


def _build_filters(search_params: OrganizationSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.name:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_name otn
                WHERE otn.organization_id = ov.id
                  AND otn.search_vector @@ websearch_to_tsquery('english', %(name_query)s)
            )
            """
        )
        params["name_query"] = search_params.name.upper()

    if search_params.identifier:
        system, identifier_value = _parse_identifier_query(search_params.identifier)
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
                        WHERE co.organization_id = ov.id
                          AND co.npi = %(identifier_npi)s
                    )
                    """
                )
                params["identifier_npi"] = npi_value
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
                        WHERE co.organization_id = ov.id
                          AND co.npi = %(identifier_npi)s
                    )
                    """
                )
                params["identifier_npi"] = npi_value

            try:
                ein_uuid = UUID(identifier_value)
            except (TypeError, ValueError):
                ein_uuid = None
            if ein_uuid is not None:
                identifier_clauses.append("ov.ein_id = %(identifier_ein)s::uuid")
                params["identifier_ein"] = str(ein_uuid)

            identifier_clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM clinical_organization co
                    JOIN organization_to_other_id otoi ON otoi.npi = co.npi
                    WHERE co.organization_id = ov.id
                      AND otoi.other_id = %(identifier_other_id)s
                )
                """
            )
            params["identifier_other_id"] = identifier_value

            clauses.append("(" + " OR ".join(identifier_clauses) + ")")

    if search_params.organization_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM clinical_organization co
                JOIN organization_to_taxonomy ott ON ott.npi = co.npi
                JOIN nucc nu ON nu.code = ott.nucc_code
                WHERE co.organization_id = ov.id
                  AND nu.search_vector @@ websearch_to_tsquery('english', %(organization_type_query)s)
            )
            """
        )
        params["organization_type_query"] = search_params.organization_type

    if search_params.address:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_address ota
                JOIN address a ON a.id = ota.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ota.organization_id = ov.id
                  AND au.search_vector @@ websearch_to_tsquery('english', %(address_query)s)
            )
            """
        )
        params["address_query"] = search_params.address

    if search_params.address_city:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_address ota
                JOIN address a ON a.id = ota.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ota.organization_id = ov.id
                  AND au.city_name = %(address_city)s
            )
            """
        )
        params["address_city"] = search_params.address_city

    if search_params.address_state:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_address ota
                JOIN address a ON a.id = ota.address_id
                JOIN address_us au ON au.id = a.address_us_id
                JOIN fips_state fs ON fs.id = au.state_code
                WHERE ota.organization_id = ov.id
                  AND fs.abbreviation = %(address_state)s
            )
            """
        )
        params["address_state"] = search_params.address_state

    if search_params.address_postalcode:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM organization_to_address ota
                JOIN address a ON a.id = ota.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ota.organization_id = ov.id
                  AND au.zipcode = %(address_postalcode)s
            )
            """
        )
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
                    WHERE ota.organization_id = ov.id
                      AND ota.address_use_id = %(address_use_id)s
                )
                """
            )
            params["address_use_id"] = address_use_id

    if not clauses:
        return SqlFilter(where_sql="", params=params)

    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "name": "ov.name",
    }

    if not sort_param:
        return "ORDER BY ov.name"

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
        return "ORDER BY ov.name"
    return "ORDER BY " + ", ".join(fields)


def _fetch_organization_names(organization_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not organization_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            otn.organization_id,
            otn.name,
            otn.is_primary
        FROM organization_to_name otn
        WHERE otn.organization_id = ANY(%(organization_ids)s::uuid[])
        ORDER BY otn.organization_id, otn.name
        """,
        {"organization_ids": organization_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["organization_id"]].append(row)
    return grouped


def _fetch_organization_addresses(organization_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not organization_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            ota.organization_id,
            ota.address_id,
            ota.address_use_id,
            fau.value AS address_use_value,
            au.delivery_line_1,
            au.delivery_line_2,
            au.city_name,
            fs.abbreviation AS state_abbreviation,
            au.zipcode
        FROM organization_to_address ota
        JOIN fhir_address_use fau ON fau.id = ota.address_use_id
        JOIN address a ON a.id = ota.address_id
        JOIN address_us au ON au.id = a.address_us_id
        JOIN fips_state fs ON fs.id = au.state_code
        WHERE ota.organization_id = ANY(%(organization_ids)s::uuid[])
        ORDER BY ota.organization_id, ota.address_use_id, ota.address_id
        """,
        {"organization_ids": organization_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["organization_id"]].append(row)
    return grouped


def _fetch_parent_display_names(parent_ids: list[Any]) -> dict[Any, str]:
    if not parent_ids:
        return {}
    rows = fetch_all(
        """
        SELECT DISTINCT ON (otn.organization_id)
            otn.organization_id,
            otn.name
        FROM organization_to_name otn
        WHERE otn.organization_id = ANY(%(parent_ids)s::uuid[])
        ORDER BY otn.organization_id, otn.name
        """,
        {"parent_ids": parent_ids},
    )
    return {row["organization_id"]: row["name"] for row in rows}


def _fetch_clinical_orgs(organization_ids: list[Any]) -> dict[Any, dict[str, Any]]:
    if not organization_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            co.organization_id,
            co.npi,
            n.enumeration_date,
            n.deactivation_date
        FROM clinical_organization co
        JOIN npi n ON n.npi = co.npi
        WHERE co.organization_id = ANY(%(organization_ids)s::uuid[])
        """,
        {"organization_ids": organization_ids},
    )
    return {row["organization_id"]: row for row in rows}


def _fetch_organization_other_identifiers(npi_values: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not npi_values:
        return {}
    rows = fetch_all(
        """
        SELECT
            otoi.npi,
            otoi.other_id,
            otoi.other_id_type_id,
            otoi.issuer,
            fs.abbreviation AS state_abbreviation
        FROM organization_to_other_id otoi
        JOIN fips_state fs ON fs.id = otoi.state_code
        WHERE otoi.npi = ANY(%(npi_values)s::bigint[])
        ORDER BY otoi.npi, otoi.other_id_type_id, otoi.other_id, otoi.issuer
        """,
        {"npi_values": npi_values},
    )
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["npi"]].append(row)
    return grouped


def _fetch_organization_taxonomies(npi_values: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not npi_values:
        return {}
    rows = fetch_all(
        """
        SELECT
            ott.npi,
            ott.nucc_code,
            nu.display_name
        FROM organization_to_taxonomy ott
        JOIN nucc nu ON nu.code = ott.nucc_code
        WHERE ott.npi = ANY(%(npi_values)s::bigint[])
        ORDER BY ott.npi, ott.nucc_code
        """,
        {"npi_values": npi_values},
    )
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["npi"]].append(row)
    return grouped


def _build_taxonomy_extension(row: Mapping[str, Any]) -> dict[str, Any]:
    code = CodeableConcept(
        coding=[
            Coding(
                system="http://nucc.org/provider-taxonomy",
                code=row["nucc_code"],
                display=row["display_name"],
            )
        ]
    )
    return Extension(
        url="https://build.fhir.org/organization-definitions.html#Organization.qualification",
        valueCodeableConcept=code,
    ).model_dump()


def _build_organization_resource(
    base_row: Mapping[str, Any],
    *,
    base_url: str,
    names: list[Mapping[str, Any]],
    addresses: list[Mapping[str, Any]],
    parent_display_name: str | None,
    clinical_org: Mapping[str, Any] | None,
    other_identifiers: list[Mapping[str, Any]],
    taxonomies: list[Mapping[str, Any]],
    authorized_official_names: list[Mapping[str, Any]],
    authorized_official_phones: list[Mapping[str, Any]],
    authorized_official_emails: list[Mapping[str, Any]],
) -> dict[str, Any]:
    organization = FHIROrganization()
    organization.id = str(base_row["organization_id"])
    organization.meta = Meta(profile=[ORGANIZATION_PROFILE_URL])

    identifiers: list[dict[str, Any]] = []
    if clinical_org is not None:
        identifiers.append(_build_npi_identifier(clinical_org))
        identifiers.extend(_build_other_identifier(row) for row in other_identifiers)
    organization.identifier = identifiers

    taxonomy_extensions = [_build_taxonomy_extension(row) for row in taxonomies]
    if taxonomy_extensions:
        organization.extension = taxonomy_extensions

    rendered_names = [dict(row) for row in names]
    primary_names = [(i, n) for i, n in enumerate(rendered_names) if n["is_primary"]]
    aliases: list[dict[str, Any]] = []
    if primary_names:
        organization.name = primary_names[0][1]["name"]
        primary_name_index = primary_names[0][0]
        del rendered_names[primary_name_index]
        aliases = rendered_names
    elif rendered_names:
        organization.name = rendered_names[0]
        if len(rendered_names) > 1:
            aliases = rendered_names[1:]
    if aliases:
        organization.alias = [row["name"] for row in aliases]

    if base_row["parent_id"] is not None:
        organization.partOf = _organization_reference(
            base_url,
            base_row["parent_id"],
            display=parent_display_name,
        )

    rendered_addresses = [_build_address(row) for row in addresses]
    if base_row["authorized_official_id"] is not None:
        authorized_official = {
            "name": [_build_name(row) for row in authorized_official_names],
            "telecom": [_build_phone(row) for row in authorized_official_phones]
            + [_build_email(row) for row in authorized_official_emails],
        }
        authorized_official["name"] = authorized_official["name"][0]
        if rendered_addresses != []:
            authorized_official["address"] = rendered_addresses[0]
        else:
            if "address" in authorized_official:
                del authorized_official["address"]
        organization.contact = [authorized_official]

    return organization.model_dump()


def _load_organization_resources(
    base_rows: list[dict[str, Any]],
    *,
    base_url: str,
) -> list[dict[str, Any]]:
    organization_ids = [row["organization_id"] for row in base_rows]
    parent_ids = [row["parent_id"] for row in base_rows if row["parent_id"] is not None]
    authorized_official_ids = [
        row["authorized_official_id"]
        for row in base_rows
        if row["authorized_official_id"] is not None
    ]

    organization_names = _fetch_organization_names(organization_ids)
    organization_addresses = _fetch_organization_addresses(organization_ids)
    parent_display_names = _fetch_parent_display_names(parent_ids)
    clinical_orgs = _fetch_clinical_orgs(organization_ids)
    npi_values = [row["npi"] for row in clinical_orgs.values()]
    organization_other_identifiers = _fetch_organization_other_identifiers(npi_values)
    organization_taxonomies = _fetch_organization_taxonomies(npi_values)
    authorized_official_names = _fetch_related_names(authorized_official_ids)
    authorized_official_phones = _fetch_related_phones(authorized_official_ids)
    authorized_official_emails = _fetch_related_emails(authorized_official_ids)

    resources: list[dict[str, Any]] = []
    for base_row in base_rows:
        clinical_org = clinical_orgs.get(base_row["organization_id"])
        clinical_org_npi = clinical_org["npi"] if clinical_org is not None else None
        resources.append(
            _build_organization_resource(
                base_row,
                base_url=base_url,
                names=organization_names.get(base_row["organization_id"], []),
                addresses=organization_addresses.get(base_row["organization_id"], []),
                parent_display_name=parent_display_names.get(base_row["parent_id"]),
                clinical_org=clinical_org,
                other_identifiers=organization_other_identifiers.get(clinical_org_npi, []),
                taxonomies=organization_taxonomies.get(clinical_org_npi, []),
                authorized_official_names=authorized_official_names.get(
                    base_row["authorized_official_id"], []
                ),
                authorized_official_phones=authorized_official_phones.get(
                    base_row["authorized_official_id"], []
                ),
                authorized_official_emails=authorized_official_emails.get(
                    base_row["authorized_official_id"], []
                ),
            )
        )
    return resources


def list_organization_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
    base_url: str,
) -> OrganizationListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {_ORGANIZATION_BASE_FROM}
        {sql_filter.where_sql}
        """,
        sql_params,
    )
    if total_count is None:
        total_count = 0

    sql_params.update(
        {
            "limit": page_size,
            "offset": (page - 1) * page_size,
        }
    )
    base_rows = fetch_all(
        f"""
        {_ORGANIZATION_BASE_SELECT}
        {_ORGANIZATION_BASE_FROM}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s
        OFFSET %(offset)s
        """,
        sql_params,
    )
    resources = _load_organization_resources(base_rows, base_url=base_url)
    return OrganizationListResult(resources=resources, total_count=int(total_count))


def get_organization_resource(organization_id: str, *, base_url: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_ORGANIZATION_BASE_SELECT}
        {_ORGANIZATION_BASE_FROM}
        WHERE ov.id = %(organization_id)s::uuid
        LIMIT 1
        """,
        {"organization_id": organization_id},
    )
    if base_row is None:
        return None

    return _load_organization_resources([base_row], base_url=base_url)[0]
