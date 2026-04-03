"""Lookup and assemble practitioner profiles from the ETL CoreDM schema."""

from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Callable, Mapping
from datetime import date
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from .etl_db import fetch_all

FetchAllFn = Callable[[str, Mapping[str, Any] | None], list[dict[str, Any]]]


class ServiceModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class PractitionerMatchInput(ServiceModel):
    first_name: str
    last_name: str
    date_of_birth: date
    ssn: str


class PersonName(ServiceModel):
    person_name_id: UUID
    prefix: str | None = None
    first_name: str
    middle_name: str | None = None
    last_name: str
    suffix: str | None = None
    full_name: str | None = None
    name_type: str | None = None
    is_primary: bool = False
    effective_start_date: date | None = None
    effective_end_date: date | None = None


class TaxonomySummary(ServiceModel):
    taxonomy_code_id: UUID
    code: str
    display_name: str | None = None
    definition: str | None = None
    source_system: str | None = None


class PhoneNumber(ServiceModel):
    country_code: str | None = None
    area_code: str | None = None
    phone_number: str
    phone_extension: str | None = None
    phone_type: str | None = None
    is_primary: bool | None = None


class NpiIdentifier(ServiceModel):
    npi_identifier_id: UUID
    npi_id: int
    identifier_type_id: UUID | None = None
    identifier_type_name: str | None = None
    identifier_type_description: str | None = None
    code: str
    assigner_organization_id: UUID | None = None
    assigner_name: str | None = None


class PractitionerNpiRecord(ServiceModel):
    practitioner_npi_id: UUID
    npi_id: int
    is_sole_proprietor: bool | None = None
    npi_type: str | None = None
    replacement_npi_id: int | None = None
    entity_type_code: str | None = None
    entity_type_description: str | None = None
    enumeration_date: date | None = None
    last_update_date: date | None = None
    certification_date: date | None = None
    credential_text: str | None = None
    gender: str | None = None
    deactivation_reason_code: str | None = None
    deactivation_date: str | None = None
    reactivation_date: str | None = None
    identifiers: list[NpiIdentifier] = Field(default_factory=list)
    phone_numbers: list[PhoneNumber] = Field(default_factory=list)


class StateLicense(ServiceModel):
    state_license_id: UUID
    npi_id: int | None = None
    state_code: str
    license_number: str


class ProfessionalCredential(ServiceModel):
    prof_cred_id: UUID
    organization_id: UUID | None = None
    npi_id: int | None = None
    jurisdiction_id: UUID | None = None
    jurisdiction_code: str | None = None
    jurisdiction_name: str | None = None
    credential_type: str
    prof_cred_code: str | None = None
    prof_cred_status: str | None = None
    is_primary: bool | None = None
    prof_cred_effective_date: date | None = None
    issue_date: date | None = None
    expiration_date: date | None = None
    state_license: StateLicense | None = None
    taxonomy: TaxonomySummary | None = None


class PractitionerRole(ServiceModel):
    practitioner_role_id: UUID
    role_type: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    is_current: bool | None = None
    has_nppes: bool | None = None
    has_pecos: bool | None = None
    authoritative_source: str | None = None
    taxonomy: TaxonomySummary | None = None


class LegalEntitySummary(ServiceModel):
    legal_entity_id: UUID
    name: str | None = None
    entity_type: str | None = None
    org_category: str | None = None
    is_operating: bool | None = None


class LocationAddress(ServiceModel):
    address_type: str
    line1: str | None = None
    line2: str | None = None
    city: str | None = None
    state_or_region: str | None = None
    postal_code: str | None = None
    country: str | None = None
    raw_text: str | None = None


class LocationProfile(ServiceModel):
    location_id: UUID
    practitioner_to_location_id: UUID | None = None
    practitioner_to_organization_id: UUID | None = None
    organization_id: UUID | None = None
    practitioner_id: UUID | None = None
    npi_id: int | None = None
    address_use: str | None = None
    is_active: bool | None = None
    is_primary_organization_location: bool = False
    address: LocationAddress | None = None
    phone_number: PhoneNumber | None = None


class OrganizationAffiliation(ServiceModel):
    practitioner_to_organization_id: UUID | None = None
    organization_id: UUID
    organization_name: str | None = None
    npi_id: int | None = None
    is_active: bool | None = None
    activation_date: date | None = None
    deactivation_date: date | None = None
    legal_entity_id: UUID | None = None
    legal_entity_name: str | None = None
    primary_taxonomy: TaxonomySummary | None = None
    primary_location_id: UUID | None = None
    identifiers: list[NpiIdentifier] = Field(default_factory=list)
    phone_numbers: list[PhoneNumber] = Field(default_factory=list)
    locations: list[LocationProfile] = Field(default_factory=list)


class PractitionerProfile(ServiceModel):
    practitioner_id: UUID
    primary_name: PersonName | None = None
    names: list[PersonName] = Field(default_factory=list)
    primary_npi_id: int | None = None
    npi_records: list[PractitionerNpiRecord] = Field(default_factory=list)
    gender_code: str | None = None
    date_of_birth: date | None = None
    social_security_number_last4: str | None = None
    irs_individual_tax_identification_number_last4: str | None = None
    other_credential_text: str | None = None
    primary_organization_id: UUID | None = None
    primary_state_license_id: UUID | None = None
    legal_entity: LegalEntitySummary | None = None
    roles: list[PractitionerRole] = Field(default_factory=list)
    state_licenses: list[StateLicense] = Field(default_factory=list)
    credentials: list[ProfessionalCredential] = Field(default_factory=list)
    organizations: list[OrganizationAffiliation] = Field(default_factory=list)


class AmbiguousPractitionerMatchError(LookupError):
    """Raised when more than one practitioner matches the login identity tuple."""


def _normalize_name(value: str) -> str:
    normalized = " ".join(value.strip().split())
    if normalized == "":
        raise ValueError("Name values must not be blank.")
    return normalized.lower()


def _normalize_ssn(value: str) -> str:
    digits = re.sub(r"\D", "", value)
    if len(digits) != 9:
        raise ValueError("SSN must contain exactly 9 digits.")
    return digits


def _mask_last4(value: str | None) -> str | None:
    if value in (None, ""):
        return None
    digits = re.sub(r"\D", "", value)
    if len(digits) < 4:
        return None
    return digits[-4:]


def _taxonomy_from_row(row: Mapping[str, Any], *, prefix: str = "") -> TaxonomySummary | None:
    taxonomy_code_id = row.get(f"{prefix}taxonomy_code_id")
    code = row.get(f"{prefix}taxonomy_code")
    if taxonomy_code_id is None or code in (None, ""):
        return None

    return TaxonomySummary(
        taxonomy_code_id=taxonomy_code_id,
        code=code,
        display_name=row.get(f"{prefix}taxonomy_display_name"),
        definition=row.get(f"{prefix}taxonomy_definition"),
        source_system=row.get(f"{prefix}taxonomy_source_system"),
    )


def _phone_from_row(row: Mapping[str, Any], *, prefix: str = "") -> PhoneNumber | None:
    phone_number = row.get(f"{prefix}phone_number")
    if phone_number in (None, ""):
        return None

    return PhoneNumber(
        country_code=row.get(f"{prefix}country_code"),
        area_code=row.get(f"{prefix}area_code"),
        phone_number=phone_number,
        phone_extension=row.get(f"{prefix}phone_extension"),
        phone_type=row.get(f"{prefix}phone_type"),
        is_primary=row.get(f"{prefix}is_primary"),
    )


def _location_address_from_row(row: Mapping[str, Any]) -> LocationAddress | None:
    if row.get("location_us_id") is not None:
        postal_code = row.get("zipcode")
        plus4_code = row.get("plus4_code")
        if postal_code and plus4_code:
            postal_code = f"{postal_code}-{plus4_code}"
        return LocationAddress(
            address_type="US",
            line1=row.get("delivery_line_1"),
            line2=row.get("delivery_line_2"),
            city=row.get("city_name"),
            state_or_region=row.get("state_abbreviation"),
            postal_code=postal_code,
            country="US",
            raw_text=row.get("last_line"),
        )

    if row.get("location_nonstandard_id") is not None:
        return LocationAddress(
            address_type="NONSTANDARD",
            line1=row.get("location_line"),
            city=row.get("nonstandard_city"),
            state_or_region=row.get("nonstandard_administrative_area") or row.get("province"),
            postal_code=row.get("nonstandard_postal_code") or row.get("foreign_postal_code"),
            country=row.get("foreign_country_name"),
            raw_text=row.get("location_line"),
        )

    if row.get("location_international_id") is not None:
        return LocationAddress(
            address_type="INTERNATIONAL",
            line1=row.get("international_location"),
            city=row.get("locality"),
            state_or_region=row.get("international_administrative_area"),
            postal_code=row.get("international_postal_code"),
            country=row.get("country"),
            raw_text=row.get("international_location"),
        )

    return None


def _organization_sort_key(affiliation: OrganizationAffiliation) -> tuple[str, str]:
    return (
        affiliation.organization_name or "",
        str(affiliation.organization_id),
    )


class PractitionerProfileService:
    def __init__(self, *, fetch_all_fn: FetchAllFn = fetch_all):
        self._fetch_all = fetch_all_fn

    def lookup_practitioner_profile(
        self,
        *,
        first_name: str,
        last_name: str,
        date_of_birth: date | str,
        ssn: str,
    ) -> PractitionerProfile | None:
        lookup_input = PractitionerMatchInput.model_validate(
            {
                "first_name": first_name,
                "last_name": last_name,
                "date_of_birth": date_of_birth,
                "ssn": ssn,
            }
        )
        match_rows = self._fetch_match_rows(lookup_input)
        if match_rows == []:
            return None
        if len(match_rows) > 1:
            raise AmbiguousPractitionerMatchError(
                "More than one practitioner matched the supplied first name, last name, date of birth, and SSN."
            )

        base_row = match_rows[0]
        practitioner_id: UUID = base_row["practitioner_id"]

        names = self._fetch_names(practitioner_id)
        npi_rows = self._fetch_npi_rows(practitioner_id)
        roles = self._fetch_roles(practitioner_id)
        state_licenses = self._fetch_state_licenses(practitioner_id)
        state_license_by_id = {
            row["state_license_id"]: StateLicense.model_validate(row) for row in state_licenses
        }
        credentials = self._fetch_credentials(practitioner_id)
        affiliation_rows = self._fetch_affiliation_rows(practitioner_id)

        organization_ids = {
            row["organization_id"]
            for row in affiliation_rows
            if row.get("organization_id") is not None
        }
        if base_row.get("primary_organization_id") is not None:
            organization_ids.add(base_row["primary_organization_id"])
        for row in credentials:
            if row.get("organization_id") is not None:
                organization_ids.add(row["organization_id"])

        organizations = self._fetch_organizations(sorted(organization_ids, key=str))
        legal_entity_ids = {
            row["legal_entity_id"] for row in organizations if row.get("legal_entity_id") is not None
        }
        if base_row.get("legal_entity_id") is not None:
            legal_entity_ids.add(base_row["legal_entity_id"])
        legal_entities = self._fetch_legal_entities(sorted(legal_entity_ids, key=str))

        location_ids = {
            row["location_id"] for row in affiliation_rows if row.get("location_id") is not None
        }
        for row in organizations:
            if row.get("primary_location_id") is not None:
                location_ids.add(row["primary_location_id"])
        locations = self._fetch_locations(sorted(location_ids, key=str))

        all_npi_ids = {
            row["npi_id"] for row in npi_rows if row.get("npi_id") is not None
        }
        for row in organizations:
            if row.get("npi_id") is not None:
                all_npi_ids.add(row["npi_id"])
        npi_identifiers = self._fetch_npi_identifiers(sorted(all_npi_ids))
        npi_phone_numbers = self._fetch_npi_phone_numbers(sorted(all_npi_ids))

        names_models = [PersonName.model_validate(row) for row in names]

        npi_records = []
        for row in npi_rows:
            npi_records.append(
                PractitionerNpiRecord(
                    practitioner_npi_id=row["practitioner_npi_id"],
                    npi_id=row["npi_id"],
                    is_sole_proprietor=row.get("is_sole_proprietor"),
                    npi_type=row.get("npi_type"),
                    replacement_npi_id=row.get("replacement_npi_id"),
                    entity_type_code=row.get("entity_type_code"),
                    entity_type_description=row.get("entity_type_description"),
                    enumeration_date=row.get("enumeration_date"),
                    last_update_date=row.get("last_update_date"),
                    certification_date=row.get("certification_date"),
                    credential_text=row.get("credential_text"),
                    gender=row.get("gender"),
                    deactivation_reason_code=row.get("npi_deactivation_reason_code"),
                    deactivation_date=row.get("npi_deactivation_date"),
                    reactivation_date=row.get("npi_reactivation_date"),
                    identifiers=[
                        NpiIdentifier.model_validate(identifier_row)
                        for identifier_row in npi_identifiers.get(row["npi_id"], [])
                    ],
                    phone_numbers=[
                        phone_model
                        for phone_row in npi_phone_numbers.get(row["npi_id"], [])
                        for phone_model in [_phone_from_row(phone_row)]
                        if phone_model is not None
                    ],
                )
            )

        role_models = [
            PractitionerRole(
                practitioner_role_id=row["practitioner_role_id"],
                role_type=row.get("role_type"),
                start_date=row.get("start_date"),
                end_date=row.get("end_date"),
                is_current=row.get("is_current"),
                has_nppes=row.get("has_nppes"),
                has_pecos=row.get("has_pecos"),
                authoritative_source=row.get("authoritative_source"),
                taxonomy=_taxonomy_from_row(row),
            )
            for row in roles
        ]

        credential_models = [
            ProfessionalCredential(
                prof_cred_id=row["prof_cred_id"],
                organization_id=row.get("organization_id"),
                npi_id=row.get("npi_id"),
                jurisdiction_id=row.get("jurisdiction_id"),
                jurisdiction_code=row.get("jurisdiction_code"),
                jurisdiction_name=row.get("jurisdiction_name"),
                credential_type=row["credential_type"],
                prof_cred_code=row.get("prof_cred_code"),
                prof_cred_status=row.get("prof_cred_status"),
                is_primary=row.get("is_primary"),
                prof_cred_effective_date=row.get("prof_cred_effective_date"),
                issue_date=row.get("issue_date"),
                expiration_date=row.get("expiration_date"),
                state_license=state_license_by_id.get(row.get("state_license_id")),
                taxonomy=_taxonomy_from_row(row),
            )
            for row in credentials
        ]

        legal_entity_by_id = {
            row["legal_entity_id"]: LegalEntitySummary.model_validate(row) for row in legal_entities
        }
        organization_by_id = {row["organization_id"]: row for row in organizations}
        location_by_id = {row["location_id"]: row for row in locations}

        affiliation_rows_by_id = {
            row["practitioner_to_organization"]: row
            for row in affiliation_rows
            if row.get("practitioner_to_organization") is not None
        }
        location_rows_by_affiliation: dict[UUID, list[dict[str, Any]]] = defaultdict(list)
        for row in affiliation_rows:
            practitioner_to_organization = row.get("practitioner_to_organization")
            if practitioner_to_organization is None or row.get("location_id") is None:
                continue
            location_rows_by_affiliation[practitioner_to_organization].append(row)

        affiliations: dict[UUID, OrganizationAffiliation] = {}
        for row in affiliation_rows:
            organization_id = row.get("organization_id")
            if organization_id is None:
                continue
            if organization_id in affiliations:
                continue

            organization_row = organization_by_id.get(organization_id, {})
            primary_taxonomy = _taxonomy_from_row(organization_row, prefix="primary_")
            affiliation = OrganizationAffiliation(
                practitioner_to_organization_id=row.get("practitioner_to_organization"),
                organization_id=organization_id,
                organization_name=organization_row.get("organization_name"),
                npi_id=organization_row.get("npi_id"),
                is_active=organization_row.get("is_active"),
                activation_date=organization_row.get("activation_date"),
                deactivation_date=organization_row.get("deactivation_date"),
                legal_entity_id=organization_row.get("legal_entity_id"),
                legal_entity_name=organization_row.get("legal_entity_name"),
                primary_taxonomy=primary_taxonomy,
                primary_location_id=organization_row.get("primary_location_id"),
                identifiers=[
                    NpiIdentifier.model_validate(identifier_row)
                    for identifier_row in npi_identifiers.get(organization_row.get("npi_id"), [])
                ],
                phone_numbers=[
                    phone_model
                    for phone_row in npi_phone_numbers.get(organization_row.get("npi_id"), [])
                    for phone_model in [_phone_from_row(phone_row)]
                    if phone_model is not None
                ],
            )
            affiliations[organization_id] = affiliation

        for organization_row in organizations:
            organization_id = organization_row["organization_id"]
            if organization_id in affiliations:
                continue
            affiliation = OrganizationAffiliation(
                practitioner_to_organization_id=None,
                organization_id=organization_id,
                organization_name=organization_row.get("organization_name"),
                npi_id=organization_row.get("npi_id"),
                is_active=organization_row.get("is_active"),
                activation_date=organization_row.get("activation_date"),
                deactivation_date=organization_row.get("deactivation_date"),
                legal_entity_id=organization_row.get("legal_entity_id"),
                legal_entity_name=organization_row.get("legal_entity_name"),
                primary_taxonomy=_taxonomy_from_row(organization_row, prefix="primary_"),
                primary_location_id=organization_row.get("primary_location_id"),
                identifiers=[
                    NpiIdentifier.model_validate(identifier_row)
                    for identifier_row in npi_identifiers.get(organization_row.get("npi_id"), [])
                ],
                phone_numbers=[
                    phone_model
                    for phone_row in npi_phone_numbers.get(organization_row.get("npi_id"), [])
                    for phone_model in [_phone_from_row(phone_row)]
                    if phone_model is not None
                ],
            )
            affiliations[organization_id] = affiliation

        for affiliation in affiliations.values():
            relationship_row = None
            if affiliation.practitioner_to_organization_id is not None:
                relationship_row = affiliation_rows_by_id.get(affiliation.practitioner_to_organization_id)

            seen_location_ids: set[UUID] = set()
            if relationship_row is not None:
                for location_row in location_rows_by_affiliation.get(
                    relationship_row["practitioner_to_organization"], []
                ):
                    raw_location = location_by_id.get(location_row["location_id"])
                    if raw_location is None:
                        continue
                    affiliation.locations.append(
                        LocationProfile(
                            location_id=raw_location["location_id"],
                            practitioner_to_location_id=location_row.get(
                                "practitioner_to_location_id"
                            ),
                            practitioner_to_organization_id=location_row.get(
                                "practitioner_to_organization"
                            ),
                            organization_id=raw_location.get("organization_id"),
                            practitioner_id=raw_location.get("practitioner_id"),
                            npi_id=raw_location.get("npi_id"),
                            address_use=raw_location.get("address_use"),
                            is_active=location_row.get("is_active"),
                            is_primary_organization_location=(
                                raw_location["location_id"] == affiliation.primary_location_id
                            ),
                            address=_location_address_from_row(raw_location),
                            phone_number=_phone_from_row(raw_location, prefix="location_"),
                        )
                    )
                    seen_location_ids.add(raw_location["location_id"])

            if affiliation.primary_location_id is not None and affiliation.primary_location_id not in seen_location_ids:
                raw_location = location_by_id.get(affiliation.primary_location_id)
                if raw_location is not None:
                    affiliation.locations.append(
                        LocationProfile(
                            location_id=raw_location["location_id"],
                            practitioner_to_location_id=None,
                            practitioner_to_organization_id=affiliation.practitioner_to_organization_id,
                            organization_id=raw_location.get("organization_id"),
                            practitioner_id=raw_location.get("practitioner_id"),
                            npi_id=raw_location.get("npi_id"),
                            address_use=raw_location.get("address_use"),
                            is_active=None,
                            is_primary_organization_location=True,
                            address=_location_address_from_row(raw_location),
                            phone_number=_phone_from_row(raw_location, prefix="location_"),
                        )
                    )

            affiliation.locations.sort(key=lambda location: str(location.location_id))

        organizations_list = sorted(affiliations.values(), key=_organization_sort_key)

        return PractitionerProfile(
            practitioner_id=practitioner_id,
            primary_name=names_models[0] if names_models != [] else None,
            names=names_models,
            primary_npi_id=base_row.get("primary_npi_id"),
            npi_records=npi_records,
            gender_code=base_row.get("gender_code"),
            date_of_birth=base_row.get("date_of_birth"),
            social_security_number_last4=_mask_last4(
                base_row.get("social_security_number_last4")
            ),
            irs_individual_tax_identification_number_last4=_mask_last4(
                base_row.get("irs_individual_tax_identification_number_last4")
            ),
            other_credential_text=base_row.get("other_credential_text"),
            primary_organization_id=base_row.get("primary_organization_id"),
            primary_state_license_id=base_row.get("primary_state_license_id"),
            legal_entity=legal_entity_by_id.get(base_row.get("legal_entity_id")),
            roles=role_models,
            state_licenses=list(state_license_by_id.values()),
            credentials=credential_models,
            organizations=organizations_list,
        )

    def _fetch_match_rows(self, lookup_input: PractitionerMatchInput) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT DISTINCT ON (p.practitioner_id)
                p.practitioner_id,
                p.organization_id AS primary_organization_id,
                p.legal_entity_id,
                p.npi_id AS primary_npi_id,
                p.state_license_id AS primary_state_license_id,
                p.gender_code,
                p.date_of_birth,
                RIGHT(REGEXP_REPLACE(COALESCE(p.social_security_number, ''), '\\D', '', 'g'), 4) AS social_security_number_last4,
                RIGHT(REGEXP_REPLACE(COALESCE(p.irs_individual_tax_identification_number, ''), '\\D', '', 'g'), 4) AS irs_individual_tax_identification_number_last4,
                p.other_credential_text
            FROM practitioner p
            JOIN person_names pn
              ON pn.practitioner_id = p.practitioner_id
             AND pn.is_primary IS TRUE
            WHERE LOWER(REGEXP_REPLACE(BTRIM(pn.first_name), '\\s+', ' ', 'g')) = %(first_name)s
              AND LOWER(REGEXP_REPLACE(BTRIM(pn.last_name), '\\s+', ' ', 'g')) = %(last_name)s
              AND p.date_of_birth = %(date_of_birth)s
              AND REGEXP_REPLACE(COALESCE(p.social_security_number, ''), '\\D', '', 'g') = %(ssn)s
            ORDER BY p.practitioner_id
            LIMIT 2
            """,
            {
                "first_name": _normalize_name(lookup_input.first_name),
                "last_name": _normalize_name(lookup_input.last_name),
                "date_of_birth": lookup_input.date_of_birth,
                "ssn": _normalize_ssn(lookup_input.ssn),
            },
        )

    def _fetch_names(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        rows = self._fetch_all(
            """
            SELECT
                person_name_id,
                name_prefix AS prefix,
                first_name,
                middle_name,
                last_name,
                name_suffix AS suffix,
                full_name,
                name_type,
                is_primary,
                effective_start_date,
                effective_end_date
            FROM person_names
            WHERE practitioner_id = %(practitioner_id)s::uuid
            ORDER BY is_primary DESC, effective_start_date NULLS LAST, full_name, person_name_id
            """,
            {"practitioner_id": practitioner_id},
        )
        return rows

    def _fetch_npi_rows(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                pn.practitioner_npi_id,
                pn.npi_id,
                COALESCE(pn.is_sole_proprietor, n.is_sole_proprietor) AS is_sole_proprietor,
                n.npi_type,
                n.replacement_npi_id,
                n.entity_type_code,
                n.entity_type_description,
                n.enumeration_date,
                n.last_update_date,
                n.certification_date,
                n.credential_text,
                n.gender,
                n.npi_deactivation_reason_code,
                n.npi_deactivation_date,
                n.npi_reactivation_date
            FROM practitioner_npi pn
            JOIN npi n ON n.npi_id = pn.npi_id
            WHERE pn.practitioner_id = %(practitioner_id)s::uuid
            ORDER BY pn.npi_id
            """,
            {"practitioner_id": practitioner_id},
        )

    def _fetch_npi_identifiers(
        self, npi_ids: list[int]
    ) -> dict[int, list[dict[str, Any]]]:
        if npi_ids == []:
            return {}

        rows = self._fetch_all(
            """
            SELECT
                ni.npi_identifier_id,
                ni.npi_id,
                ni.identifier_type_id,
                it.name AS identifier_type_name,
                it.description AS identifier_type_description,
                ni.code,
                ni.assigner_organization_id,
                ao.organization_name AS assigner_name
            FROM npi_identifier ni
            LEFT JOIN identifier_type it ON it.identifier_type_id = ni.identifier_type_id
            LEFT JOIN organization ao ON ao.organization_id = ni.assigner_organization_id
            WHERE ni.npi_id = ANY(%(npi_ids)s::bigint[])
            ORDER BY ni.npi_id, it.name NULLS LAST, ni.code
            """,
            {"npi_ids": npi_ids},
        )

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row["npi_id"]].append(row)
        return grouped

    def _fetch_npi_phone_numbers(
        self, npi_ids: list[int]
    ) -> dict[int, list[dict[str, Any]]]:
        if npi_ids == []:
            return {}

        rows = self._fetch_all(
            """
            SELECT
                npn.npi_id,
                pn.country_code,
                pn.area_code,
                pn.phone_number,
                pn.phone_extension,
                pn.phone_type,
                npn.is_primary
            FROM npi_phone_number npn
            JOIN phone_number pn ON pn.phone_number_id = npn.phone_number_id
            WHERE npn.npi_id = ANY(%(npi_ids)s::bigint[])
            ORDER BY npn.npi_id, npn.is_primary DESC, pn.phone_type NULLS LAST, pn.phone_number
            """,
            {"npi_ids": npi_ids},
        )

        grouped: dict[int, list[dict[str, Any]]] = defaultdict(list)
        for row in rows:
            grouped[row["npi_id"]].append(row)
        return grouped

    def _fetch_roles(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                pr.practitioner_role_id,
                pr.role_type,
                pr.start_date,
                pr.end_date,
                pr.is_current,
                pr.has_nppes,
                pr.has_pecos,
                pr.authoritative_source,
                tc.taxonomy_code_id,
                tc.code AS taxonomy_code,
                tc.display_name AS taxonomy_display_name,
                tc.definition AS taxonomy_definition,
                tc.source_system AS taxonomy_source_system
            FROM practitioner_role pr
            LEFT JOIN taxonomy_code tc ON tc.taxonomy_code_id = pr.taxonomy_code_id
            WHERE pr.practitioner_id = %(practitioner_id)s::uuid
            ORDER BY pr.is_current DESC, tc.code NULLS LAST, pr.practitioner_role_id
            """,
            {"practitioner_id": practitioner_id},
        )

    def _fetch_state_licenses(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                state_license_id,
                npi_id,
                state_code,
                license_number
            FROM state_license
            WHERE practitioner_id = %(practitioner_id)s::uuid
            ORDER BY state_code, license_number, state_license_id
            """,
            {"practitioner_id": practitioner_id},
        )

    def _fetch_credentials(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                pc.prof_cred_id,
                pc.organization_id,
                pc.npi_id,
                pc.jurisdiction_id,
                j.jurisdiction_code,
                j.jurisdiction_name,
                pc.credential_type,
                pc.prof_cred_code,
                pc.prof_cred_status,
                pc.is_primary,
                pc.prof_cred_effective_date,
                pc.issue_date,
                pc.expiration_date,
                pc.state_license_id,
                tc.taxonomy_code_id,
                tc.code AS taxonomy_code,
                tc.display_name AS taxonomy_display_name,
                tc.definition AS taxonomy_definition,
                tc.source_system AS taxonomy_source_system
            FROM prof_cred pc
            LEFT JOIN jurisdiction j ON j.jurisdiction_id = pc.jurisdiction_id
            LEFT JOIN taxonomy_code tc ON tc.taxonomy_code_id = pc.taxonomy_code_id
            WHERE pc.practitioner_id = %(practitioner_id)s::uuid
            ORDER BY pc.is_primary DESC, pc.credential_type, pc.prof_cred_code NULLS LAST, pc.prof_cred_id
            """,
            {"practitioner_id": practitioner_id},
        )

    def _fetch_affiliation_rows(self, practitioner_id: UUID) -> list[dict[str, Any]]:
        return self._fetch_all(
            """
            SELECT
                pto.practitioner_to_organization,
                pto.organization_id,
                ptl.practitioner_to_location AS practitioner_to_location_id,
                ptl.location_id,
                ptl.is_active
            FROM practitioner_to_organization pto
            LEFT JOIN practitioner_to_location ptl
              ON ptl.practitioner_to_organization = pto.practitioner_to_organization
            WHERE pto.practitioner_id = %(practitioner_id)s::uuid
            ORDER BY pto.organization_id, ptl.location_id NULLS LAST, ptl.practitioner_to_location
            """,
            {"practitioner_id": practitioner_id},
        )

    def _fetch_organizations(self, organization_ids: list[UUID]) -> list[dict[str, Any]]:
        if organization_ids == []:
            return []

        return self._fetch_all(
            """
            SELECT
                o.organization_id,
                o.organization_name,
                o.npi_id,
                o.is_active,
                o.activation_date,
                o.deactivation_date,
                o.legal_entity_id,
                o.location_id AS primary_location_id,
                len.name AS legal_entity_name,
                tc.taxonomy_code_id AS primary_taxonomy_code_id,
                tc.code AS primary_taxonomy_code,
                tc.display_name AS primary_taxonomy_display_name,
                tc.definition AS primary_taxonomy_definition,
                tc.source_system AS primary_taxonomy_source_system
            FROM organization o
            LEFT JOIN legal_entity_names len ON len.legal_entity_name_id = o.legal_entity_name_id
            LEFT JOIN taxonomy_code tc ON tc.taxonomy_code_id = o.primary_taxonomy_code_id
            WHERE o.organization_id = ANY(%(organization_ids)s::uuid[])
            ORDER BY o.organization_name NULLS LAST, o.organization_id
            """,
            {"organization_ids": organization_ids},
        )

    def _fetch_legal_entities(self, legal_entity_ids: list[UUID]) -> list[dict[str, Any]]:
        if legal_entity_ids == []:
            return []

        return self._fetch_all(
            """
            SELECT
                le.legal_entity_id,
                COALESCE(len.name, le.name) AS name,
                le.entity_type,
                le.org_category,
                le.is_operating
            FROM legal_entity le
            LEFT JOIN legal_entity_names len
              ON len.legal_entity_name_id = le.legal_entity_name_id
            WHERE le.legal_entity_id = ANY(%(legal_entity_ids)s::uuid[])
            ORDER BY COALESCE(len.name, le.name) NULLS LAST, le.legal_entity_id
            """,
            {"legal_entity_ids": legal_entity_ids},
        )

    def _fetch_locations(self, location_ids: list[UUID]) -> list[dict[str, Any]]:
        if location_ids == []:
            return []

        return self._fetch_all(
            """
            SELECT
                l.location_id,
                l.location_us_id,
                l.location_nonstandard_id,
                l.location_international_id,
                l.organization_id,
                l.practitioner_id,
                l.npi_id,
                l.address_use,
                lus.delivery_line_1,
                lus.delivery_line_2,
                lus.last_line,
                lus.city_name,
                lus.state_abbreviation,
                lus.zipcode,
                lus.plus4_code,
                lns.location_line,
                lns.city AS nonstandard_city,
                lns.administrative_area AS nonstandard_administrative_area,
                lns.postal_code AS nonstandard_postal_code,
                lns.province,
                lns.foreign_postal_code,
                lns.foreign_country_name,
                lin.location AS international_location,
                lin.locality,
                lin.administrative_area AS international_administrative_area,
                lin.postal_code AS international_postal_code,
                lin.country,
                pn.country_code AS location_country_code,
                pn.area_code AS location_area_code,
                pn.phone_number AS location_phone_number,
                pn.phone_extension AS location_phone_extension,
                pn.phone_type AS location_phone_type
            FROM location l
            LEFT JOIN location_us lus ON lus.location_us_id = l.location_us_id
            LEFT JOIN location_nonstandard lns ON lns.location_nonstandard_id = l.location_nonstandard_id
            LEFT JOIN location_international lin ON lin.location_international_id = l.location_international_id
            LEFT JOIN phone_number pn
              ON pn.phone_number_id = COALESCE(lus.phone_number_id, lns.phone_number_id, lin.phone_number_id)
            WHERE l.location_id = ANY(%(location_ids)s::uuid[])
            ORDER BY l.location_id
            """,
            {"location_ids": location_ids},
        )
