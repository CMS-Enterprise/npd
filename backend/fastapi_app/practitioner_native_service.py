"""Django-free Practitioner query helpers using psycopg and direct SQL."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Mapping

from fhir.resources.R4B.address import Address
from fhir.resources.R4B.codeableconcept import CodeableConcept
from fhir.resources.R4B.coding import Coding
from fhir.resources.R4B.contactpoint import ContactPoint
from fhir.resources.R4B.humanname import HumanName
from fhir.resources.R4B.identifier import Identifier
from fhir.resources.R4B.meta import Meta
from fhir.resources.R4B.period import Period
from fhir.resources.R4B.practitioner import Practitioner, PractitionerQualification
from fhir.resources.R4B.reference import Reference

from .db import fetch_all, fetch_one, fetch_scalar


PRACTITIONER_PROFILE_URL = "http://hl7.org/fhir/us/core/StructureDefinition/us-core-practitioner"
GENDER_TO_NPD = {
    "Female": "F",
    "Male": "M",
    "Other": "O",
}
ADDRESS_USE_TO_NPD = {
    "home": 1,
    "work": 2,
    "temp": 3,
    "old": 4,
    "billing": 5,
}
OTHER_ID_TYPE_TO_FHIR = {
    2: {
        "code": "UPIN",
        "display": "Medicare/CMS (formerly HCFA)'s Universal Physician Identification numbers",
    },
    4: {"code": "MCR", "display": "Practitioner Medicare Number"},
    5: {"code": "MCD", "display": "Practitioner Medicaid Number"},
    6: {"code": "MCR", "display": "Practitioner Medicare Number"},
    7: {"code": "MCR", "display": "Practitioner Medicare Number"},
    8: {"code": "PPIN", "display": "Medicare/CMS Performing Provider Identification Number"},
}


@dataclass(frozen=True)
class PractitionerListResult:
    resources: list[dict]
    total_count: int


@dataclass(frozen=True)
class PractitionerSearchParams:
    identifier: str | None
    name: str | None
    gender: str | None
    practitioner_type: str | None
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


_PRACTITIONER_BASE_FROM = """
FROM provider_view pv
JOIN provider p ON p.individual_id = pv.individual_id
JOIN individual i ON i.id = p.individual_id
JOIN npi n ON n.npi = p.npi
"""

_PRACTITIONER_BASE_SELECT = """
SELECT
    pv.individual_id AS provider_id,
    pv.npi,
    pv.first_name,
    pv.last_name,
    i.gender,
    n.enumeration_date,
    n.deactivation_date
"""

_PRACTITIONER_COUNT_FROM = """
FROM provider_view pv
"""


def _parse_identifier_query(identifier_value: str) -> tuple[str | None, str]:
    if "|" in identifier_value:
        system, value = identifier_value.split("|", 1)
        return (system, value)
    return (None, identifier_value)


def _other_id_type_to_fhir(other_id_type_id: int) -> dict[str, str]:
    return OTHER_ID_TYPE_TO_FHIR.get(other_id_type_id, {"code": "OTHER", "display": "Other"})


def _parse_search_params(query_params: Mapping[str, str]) -> PractitionerSearchParams:
    return PractitionerSearchParams(
        identifier=query_params.get("identifier"),
        name=query_params.get("name"),
        gender=query_params.get("gender"),
        practitioner_type=query_params.get("practitioner_type"),
        address=query_params.get("address"),
        address_city=query_params.get("address_city"),
        address_state=query_params.get("address_state"),
        address_postalcode=query_params.get("address_postalcode"),
        address_use=query_params.get("address_use"),
        sort=query_params.get("_sort"),
    )


def _build_filters(search_params: PractitionerSearchParams) -> SqlFilter:
    clauses: list[str] = []
    params: dict[str, Any] = {}

    if search_params.gender:
        gender_value = GENDER_TO_NPD.get(search_params.gender)
        if gender_value is not None:
            clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM individual i_filter
                    WHERE i_filter.id = pv.individual_id
                      AND i_filter.gender = %(gender)s
                )
                """
            )
            params["gender"] = gender_value

    if search_params.identifier:
        system, identifier_value = _parse_identifier_query(search_params.identifier)
        npi_value: int | None = None
        try:
            npi_value = int(identifier_value)
        except (TypeError, ValueError):
            npi_value = None

        if system is not None:
            if system.upper() == "NPI" and npi_value is not None:
                clauses.append("pv.npi = %(identifier_npi)s")
                params["identifier_npi"] = npi_value
            else:
                clauses.append("FALSE")
        else:
            identifier_clauses: list[str] = []
            if npi_value is not None:
                identifier_clauses.append("pv.npi = %(identifier_npi)s")
                params["identifier_npi"] = npi_value

            identifier_clauses.append(
                """
                EXISTS (
                    SELECT 1
                    FROM provider_to_other_id ptoi
                    WHERE ptoi.npi = pv.npi
                      AND ptoi.other_id = %(identifier_other_id)s
                )
                """
            )
            params["identifier_other_id"] = identifier_value
            clauses.append("(" + " OR ".join(identifier_clauses) + ")")

    if search_params.name:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM individual_to_name itn
                WHERE itn.individual_id = pv.individual_id
                  AND itn.search_vector @@ websearch_to_tsquery('english', %(name_query)s)
            )
            """
        )
        params["name_query"] = search_params.name

    if search_params.practitioner_type:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM provider_to_taxonomy ptt
                JOIN nucc nu ON nu.code = ptt.nucc_code
                WHERE ptt.npi = pv.npi
                  AND nu.search_vector @@ websearch_to_tsquery('english', %(taxonomy_query)s)
            )
            """
        )
        params["taxonomy_query"] = search_params.practitioner_type

    if search_params.address:
        clauses.append(
            """
            EXISTS (
                SELECT 1
                FROM individual_to_address ita
                JOIN address a ON a.id = ita.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ita.individual_id = pv.individual_id
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
                FROM individual_to_address ita
                JOIN address a ON a.id = ita.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ita.individual_id = pv.individual_id
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
                FROM individual_to_address ita
                JOIN address a ON a.id = ita.address_id
                JOIN address_us au ON au.id = a.address_us_id
                JOIN fips_state fs ON fs.id = au.state_code
                WHERE ita.individual_id = pv.individual_id
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
                FROM individual_to_address ita
                JOIN address a ON a.id = ita.address_id
                JOIN address_us au ON au.id = a.address_us_id
                WHERE ita.individual_id = pv.individual_id
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
                    FROM individual_to_address ita
                    WHERE ita.individual_id = pv.individual_id
                      AND ita.address_use_id = %(address_use_id)s
                )
                """
            )
            params["address_use_id"] = address_use_id

    if not clauses:
        return SqlFilter(where_sql="", params=params)

    return SqlFilter(where_sql="WHERE " + " AND ".join(f"({clause.strip()})" for clause in clauses), params=params)


def _build_order_by(sort_param: str | None) -> str:
    ordering_map = {
        "last_name": "pv.last_name",
        "first_name": "pv.first_name",
        "npi_value": "pv.npi",
    }

    if not sort_param:
        return "ORDER BY pv.last_name, pv.first_name"

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
        return "ORDER BY pv.last_name, pv.first_name"
    return "ORDER BY " + ", ".join(fields)


def _fetch_related_names(provider_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not provider_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            itn.individual_id AS provider_id,
            itn.prefix,
            itn.first_name,
            itn.middle_name,
            itn.last_name,
            itn.start_date,
            itn.end_date,
            itn.suffix,
            itn.name_use_id,
            fnu.value AS name_use_value
        FROM individual_to_name itn
        JOIN fhir_name_use fnu ON fnu.id = itn.name_use_id
        WHERE itn.individual_id = ANY(%(provider_ids)s::uuid[])
        ORDER BY itn.individual_id, itn.first_name, itn.middle_name, itn.last_name, itn.name_use_id
        """,
        {"provider_ids": provider_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["provider_id"]].append(row)
    return grouped


def _fetch_related_phones(provider_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not provider_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            itp.individual_id AS provider_id,
            itp.phone_number,
            itp.extension,
            itp.phone_use_id,
            fpu.value AS phone_use_value
        FROM individual_to_phone itp
        JOIN fhir_phone_use fpu ON fpu.id = itp.phone_use_id
        WHERE itp.individual_id = ANY(%(provider_ids)s::uuid[])
        ORDER BY itp.individual_id, itp.phone_number, itp.extension, itp.phone_use_id
        """,
        {"provider_ids": provider_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["provider_id"]].append(row)
    return grouped


def _fetch_related_emails(provider_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not provider_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            ite.individual_id AS provider_id,
            ite.email_address
        FROM individual_to_email ite
        WHERE ite.individual_id = ANY(%(provider_ids)s::uuid[])
        ORDER BY ite.individual_id, ite.email_address
        """,
        {"provider_ids": provider_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["provider_id"]].append(row)
    return grouped


def _fetch_related_addresses(provider_ids: list[Any]) -> dict[Any, list[dict[str, Any]]]:
    if not provider_ids:
        return {}
    rows = fetch_all(
        """
        SELECT
            ita.individual_id AS provider_id,
            ita.address_id,
            ita.address_use_id,
            fau.value AS address_use_value,
            au.delivery_line_1,
            au.delivery_line_2,
            au.city_name,
            fs.abbreviation AS state_abbreviation,
            au.zipcode
        FROM individual_to_address ita
        JOIN fhir_address_use fau ON fau.id = ita.address_use_id
        JOIN address a ON a.id = ita.address_id
        JOIN address_us au ON au.id = a.address_us_id
        JOIN fips_state fs ON fs.id = au.state_code
        WHERE ita.individual_id = ANY(%(provider_ids)s::uuid[])
        ORDER BY ita.individual_id, ita.address_use_id, ita.address_id
        """,
        {"provider_ids": provider_ids},
    )
    grouped: dict[Any, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["provider_id"]].append(row)
    return grouped


def _fetch_related_other_identifiers(npi_values: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not npi_values:
        return {}
    rows = fetch_all(
        """
        SELECT
            ptoi.npi,
            ptoi.other_id,
            ptoi.other_id_type_id,
            ptoi.issuer,
            fs.abbreviation AS state_abbreviation
        FROM provider_to_other_id ptoi
        JOIN fips_state fs ON fs.id = ptoi.state_code
        WHERE ptoi.npi = ANY(%(npi_values)s::bigint[])
        ORDER BY ptoi.npi, ptoi.other_id_type_id, ptoi.other_id, ptoi.issuer
        """,
        {"npi_values": npi_values},
    )
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["npi"]].append(row)
    return grouped


def _fetch_related_taxonomies(npi_values: list[int]) -> dict[int, list[dict[str, Any]]]:
    if not npi_values:
        return {}
    rows = fetch_all(
        """
        SELECT
            ptt.npi,
            ptt.nucc_code,
            nu.display_name
        FROM provider_to_taxonomy ptt
        JOIN nucc nu ON nu.code = ptt.nucc_code
        WHERE ptt.npi = ANY(%(npi_values)s::bigint[])
        ORDER BY ptt.npi, ptt.nucc_code
        """,
        {"npi_values": npi_values},
    )
    grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["npi"]].append(row)
    return grouped


def _build_npi_identifier(base_row: Mapping[str, Any]) -> dict[str, Any]:
    return Identifier(
        system="http://terminology.hl7.org/NamingSystem/npi",
        value=str(base_row["npi"]),
        type=CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0203",
                    code="NPI",
                    display="National Provider Identifier",
                )
            ]
        ),
        use="official",
        period=Period(
            start=base_row["enumeration_date"],
            end=base_row["deactivation_date"],
        ),
    ).model_dump()


def _build_name(row: Mapping[str, Any]) -> dict[str, Any]:
    return HumanName(
        use=row["name_use_value"],
        text=" ".join(
            part
            for part in [
                row["prefix"],
                row["first_name"],
                row["middle_name"],
                row["last_name"],
                row["suffix"],
            ]
            if part not in ("", None)
        ),
        family=row["last_name"],
        given=[row["first_name"], row["middle_name"]],
        prefix=[row["prefix"]],
        suffix=[row["suffix"]],
        period=Period(start=row["start_date"], end=row["end_date"]),
    ).model_dump()


def _build_phone(row: Mapping[str, Any]) -> dict[str, Any]:
    value = f"{row['phone_number']}"
    if row["extension"] is not None:
        value += f"ext. {row['extension']}"
    return ContactPoint(
        system="phone",
        use=row["phone_use_value"],
        value=value,
    ).model_dump()


def _build_email(row: Mapping[str, Any]) -> dict[str, Any]:
    return ContactPoint(
        system="email",
        value=row["email_address"],
    ).model_dump()


def _build_address(row: Mapping[str, Any]) -> dict[str, Any]:
    lines = [row["delivery_line_1"]]
    if row["delivery_line_2"] is not None:
        lines.append(row["delivery_line_2"])

    address = Address(
        line=lines,
        city=row["city_name"],
        state=row["state_abbreviation"],
        postalCode=row["zipcode"],
        country="US",
    )
    if row["address_use_value"] is not None:
        address.use = row["address_use_value"]
    return address.model_dump()


def _build_other_identifier(row: Mapping[str, Any]) -> dict[str, Any]:
    fhir_type = _other_id_type_to_fhir(row["other_id_type_id"])
    assigner_parts = []
    if row["issuer"] not in ("", " "):
        assigner_parts.append(row["issuer"])
    assigner_parts.append(row["state_abbreviation"])
    return Identifier(
        value=row["other_id"],
        type=CodeableConcept(
            coding=[
                Coding(
                    system="http://terminology.hl7.org/CodeSystem/v2-0203",
                    code=fhir_type["code"],
                    display=fhir_type["display"],
                )
            ]
        ),
        assigner=Reference(display=" - ".join(assigner_parts)),
    ).model_dump()


def _build_taxonomy(row: Mapping[str, Any]) -> dict[str, Any]:
    code = CodeableConcept(
        coding=[
            Coding(
                system="http://nucc.org/provider-taxonomy",
                code=row["nucc_code"],
                display=row["display_name"],
            )
        ]
    )
    return PractitionerQualification(code=code).model_dump()


def _build_practitioner_resource(
    base_row: Mapping[str, Any],
    *,
    names: list[Mapping[str, Any]],
    phones: list[Mapping[str, Any]],
    emails: list[Mapping[str, Any]],
    addresses: list[Mapping[str, Any]],
    other_identifiers: list[Mapping[str, Any]],
    taxonomies: list[Mapping[str, Any]],
) -> dict[str, Any]:
    practitioner = Practitioner()
    practitioner.id = str(base_row["provider_id"])
    practitioner.meta = Meta(profile=[PRACTITIONER_PROFILE_URL])
    practitioner.identifier = [_build_npi_identifier(base_row)] + [
        _build_other_identifier(row) for row in other_identifiers
    ]
    practitioner.name = [_build_name(row) for row in names]

    telecom = [_build_phone(row) for row in phones] + [_build_email(row) for row in emails]
    if telecom != []:
        practitioner.telecom = telecom

    rendered_addresses = [_build_address(row) for row in addresses]
    if rendered_addresses != []:
        practitioner.address = rendered_addresses

    rendered_taxonomies = [_build_taxonomy(row) for row in taxonomies]
    practitioner.qualification = rendered_taxonomies

    return practitioner.model_dump()


def _load_practitioner_resources(base_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    provider_ids = [row["provider_id"] for row in base_rows]
    npi_values = [row["npi"] for row in base_rows]

    related_names = _fetch_related_names(provider_ids)
    related_phones = _fetch_related_phones(provider_ids)
    related_emails = _fetch_related_emails(provider_ids)
    related_addresses = _fetch_related_addresses(provider_ids)
    related_other_identifiers = _fetch_related_other_identifiers(npi_values)
    related_taxonomies = _fetch_related_taxonomies(npi_values)

    resources: list[dict[str, Any]] = []
    for base_row in base_rows:
        resources.append(
            _build_practitioner_resource(
                base_row,
                names=related_names.get(base_row["provider_id"], []),
                phones=related_phones.get(base_row["provider_id"], []),
                emails=related_emails.get(base_row["provider_id"], []),
                addresses=related_addresses.get(base_row["provider_id"], []),
                other_identifiers=related_other_identifiers.get(base_row["npi"], []),
                taxonomies=related_taxonomies.get(base_row["npi"], []),
            )
        )
    return resources


def list_practitioner_resources(
    query_params: Mapping[str, str],
    *,
    page: int,
    page_size: int,
) -> PractitionerListResult:
    search_params = _parse_search_params(query_params)
    sql_filter = _build_filters(search_params)
    order_by_sql = _build_order_by(search_params.sort)
    sql_params = dict(sql_filter.params)

    total_count = fetch_scalar(
        f"""
        SELECT COUNT(*) AS total_count
        {_PRACTITIONER_COUNT_FROM}
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
        {_PRACTITIONER_BASE_SELECT}
        {_PRACTITIONER_BASE_FROM}
        {sql_filter.where_sql}
        {order_by_sql}
        LIMIT %(limit)s
        OFFSET %(offset)s
        """,
        sql_params,
    )
    resources = _load_practitioner_resources(base_rows)
    return PractitionerListResult(resources=resources, total_count=int(total_count))


def get_practitioner_resource(practitioner_id: str) -> dict[str, Any] | None:
    base_row = fetch_one(
        f"""
        {_PRACTITIONER_BASE_SELECT}
        {_PRACTITIONER_BASE_FROM}
        WHERE pv.individual_id = %(provider_id)s::uuid
        LIMIT 1
        """,
        {"provider_id": practitioner_id},
    )
    if base_row is None:
        return None

    return _load_practitioner_resources([base_row])[0]
