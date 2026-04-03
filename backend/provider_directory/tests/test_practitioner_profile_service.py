from datetime import date
from unittest import TestCase
from uuid import uuid4

from provider_directory.services.practitioner_profile_service import (
    AmbiguousPractitionerMatchError,
    PractitionerProfileService,
)


class StubFetcher:
    def __init__(self, responses):
        self.responses = responses
        self.calls = []

    def __call__(self, sql, params=None):
        self.calls.append((sql, params))
        for marker, response in self.responses:
            if marker in sql:
                return response
        raise AssertionError(f"Unexpected SQL: {sql}")


class PractitionerProfileServiceTestCase(TestCase):
    def test_lookup_builds_nested_profile_and_masks_ssn(self):
        practitioner_id = uuid4()
        primary_name_id = uuid4()
        practitioner_npi_id = uuid4()
        practitioner_role_id = uuid4()
        prof_cred_id = uuid4()
        state_license_id = uuid4()
        practitioner_to_organization_id = uuid4()
        practitioner_to_location_id = uuid4()
        organization_id = uuid4()
        legal_entity_id = uuid4()
        location_id = uuid4()
        taxonomy_code_id = uuid4()
        npi_identifier_id = uuid4()

        fetcher = StubFetcher(
            [
                (
                    "FROM practitioner p",
                    [
                        {
                            "practitioner_id": practitioner_id,
                            "primary_organization_id": organization_id,
                            "legal_entity_id": legal_entity_id,
                            "primary_npi_id": 1234567890,
                            "primary_state_license_id": state_license_id,
                            "gender_code": "F",
                            "date_of_birth": date(1980, 1, 2),
                            "social_security_number_last4": "6789",
                            "irs_individual_tax_identification_number_last4": "4321",
                            "other_credential_text": "M.D.",
                        }
                    ],
                ),
                (
                    "FROM person_names",
                    [
                        {
                            "person_name_id": primary_name_id,
                            "prefix": "Dr.",
                            "first_name": "Jane",
                            "middle_name": "Q",
                            "last_name": "Doe",
                            "suffix": None,
                            "full_name": "Dr. Jane Q Doe",
                            "name_type": "OFFICIAL",
                            "is_primary": True,
                            "effective_start_date": None,
                            "effective_end_date": None,
                        }
                    ],
                ),
                (
                    "FROM practitioner_npi pn",
                    [
                        {
                            "practitioner_npi_id": practitioner_npi_id,
                            "npi_id": 1234567890,
                            "is_sole_proprietor": False,
                            "npi_type": "NPPES",
                            "replacement_npi_id": None,
                            "entity_type_code": "1",
                            "entity_type_description": "Individual",
                            "enumeration_date": date(2015, 5, 1),
                            "last_update_date": date(2024, 1, 1),
                            "certification_date": date(2024, 1, 1),
                            "credential_text": "M.D.",
                            "gender": "F",
                            "npi_deactivation_reason_code": None,
                            "npi_deactivation_date": None,
                            "npi_reactivation_date": None,
                        }
                    ],
                ),
                (
                    "FROM npi_identifier ni",
                    [
                        {
                            "npi_identifier_id": npi_identifier_id,
                            "npi_id": 1234567890,
                            "identifier_type_id": None,
                            "identifier_type_name": "Medicaid",
                            "identifier_type_description": "State Medicaid identifier",
                            "code": "MCD-1234",
                            "assigner_organization_id": organization_id,
                            "assigner_name": "Sample Health System",
                        }
                    ],
                ),
                (
                    "FROM npi_phone_number npn",
                    [
                        {
                            "npi_id": 1234567890,
                            "country_code": "1",
                            "area_code": "212",
                            "phone_number": "2125550100",
                            "phone_extension": None,
                            "phone_type": "OFFICE",
                            "is_primary": True,
                        },
                        {
                            "npi_id": 9988776655,
                            "country_code": "1",
                            "area_code": "212",
                            "phone_number": "2125550199",
                            "phone_extension": None,
                            "phone_type": "OFFICE",
                            "is_primary": True,
                        },
                    ],
                ),
                (
                    "FROM practitioner_role pr",
                    [
                        {
                            "practitioner_role_id": practitioner_role_id,
                            "role_type": "NPPES_TAXONOMY_ROLE",
                            "start_date": None,
                            "end_date": None,
                            "is_current": True,
                            "has_nppes": True,
                            "has_pecos": False,
                            "authoritative_source": "NPPES",
                            "taxonomy_code_id": taxonomy_code_id,
                            "taxonomy_code": "207Q00000X",
                            "taxonomy_display_name": "Family Medicine Physician",
                            "taxonomy_definition": "Family medicine physician",
                            "taxonomy_source_system": "NPPES",
                        }
                    ],
                ),
                (
                    "FROM state_license",
                    [
                        {
                            "state_license_id": state_license_id,
                            "npi_id": 1234567890,
                            "state_code": "NY",
                            "license_number": "LIC-123",
                        }
                    ],
                ),
                (
                    "FROM prof_cred pc",
                    [
                        {
                            "prof_cred_id": prof_cred_id,
                            "organization_id": organization_id,
                            "npi_id": 1234567890,
                            "jurisdiction_id": None,
                            "jurisdiction_code": "NY",
                            "jurisdiction_name": "New York",
                            "credential_type": "LICENSE",
                            "prof_cred_code": "LIC-123",
                            "prof_cred_status": "ACTIVE",
                            "is_primary": True,
                            "prof_cred_effective_date": date(2021, 1, 1),
                            "issue_date": date(2021, 1, 1),
                            "expiration_date": date(2027, 1, 1),
                            "state_license_id": state_license_id,
                            "taxonomy_code_id": taxonomy_code_id,
                            "taxonomy_code": "207Q00000X",
                            "taxonomy_display_name": "Family Medicine Physician",
                            "taxonomy_definition": "Family medicine physician",
                            "taxonomy_source_system": "NPPES",
                        }
                    ],
                ),
                (
                    "FROM practitioner_to_organization pto",
                    [
                        {
                            "practitioner_to_organization": practitioner_to_organization_id,
                            "organization_id": organization_id,
                            "practitioner_to_location_id": practitioner_to_location_id,
                            "location_id": location_id,
                            "is_active": True,
                        }
                    ],
                ),
                (
                    "FROM organization o",
                    [
                        {
                            "organization_id": organization_id,
                            "organization_name": "Sample Health System",
                            "npi_id": 9988776655,
                            "is_active": True,
                            "activation_date": date(2010, 1, 1),
                            "deactivation_date": None,
                            "legal_entity_id": legal_entity_id,
                            "primary_location_id": location_id,
                            "legal_entity_name": "Sample Health Holdings",
                            "primary_taxonomy_code_id": taxonomy_code_id,
                            "primary_taxonomy_code": "261QF0400X",
                            "primary_taxonomy_display_name": "Federally Qualified Health Center",
                            "primary_taxonomy_definition": "FQHC",
                            "primary_taxonomy_source_system": "NPPES",
                        }
                    ],
                ),
                (
                    "FROM legal_entity le",
                    [
                        {
                            "legal_entity_id": legal_entity_id,
                            "name": "Sample Health Holdings",
                            "entity_type": "PRACTITIONER_ENTITY",
                            "org_category": None,
                            "is_operating": True,
                        }
                    ],
                ),
                (
                    "FROM location l",
                    [
                        {
                            "location_id": location_id,
                            "location_us_id": uuid4(),
                            "location_nonstandard_id": None,
                            "location_international_id": None,
                            "organization_id": organization_id,
                            "practitioner_id": None,
                            "npi_id": 9988776655,
                            "address_use": "work",
                            "delivery_line_1": "123 Main St",
                            "delivery_line_2": "Suite 400",
                            "last_line": "New York NY 10001",
                            "city_name": "New York",
                            "state_abbreviation": "NY",
                            "zipcode": "10001",
                            "plus4_code": "1234",
                            "location_line": None,
                            "nonstandard_city": None,
                            "nonstandard_administrative_area": None,
                            "nonstandard_postal_code": None,
                            "province": None,
                            "foreign_postal_code": None,
                            "foreign_country_name": None,
                            "international_location": None,
                            "locality": None,
                            "international_administrative_area": None,
                            "international_postal_code": None,
                            "country": None,
                            "location_country_code": "1",
                            "location_area_code": "212",
                            "location_phone_number": "2125550133",
                            "location_phone_extension": "99",
                            "location_phone_type": "OFFICE",
                        }
                    ],
                ),
            ]
        )
        service = PractitionerProfileService(fetch_all_fn=fetcher)

        profile = service.lookup_practitioner_profile(
            first_name="  JANE ",
            last_name="doe",
            date_of_birth="1980-01-02",
            ssn="123-45-6789",
        )

        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertEqual(profile.practitioner_id, practitioner_id)
        self.assertEqual(profile.social_security_number_last4, "6789")
        self.assertEqual(
            profile.irs_individual_tax_identification_number_last4,
            "4321",
        )
        self.assertEqual(profile.primary_name.full_name, "Dr. Jane Q Doe")
        self.assertEqual(profile.npi_records[0].identifiers[0].code, "MCD-1234")
        self.assertEqual(profile.npi_records[0].phone_numbers[0].phone_number, "2125550100")
        self.assertEqual(profile.roles[0].taxonomy.code, "207Q00000X")
        self.assertEqual(profile.credentials[0].state_license.license_number, "LIC-123")
        self.assertEqual(profile.legal_entity.name, "Sample Health Holdings")
        self.assertEqual(profile.organizations[0].organization_name, "Sample Health System")
        self.assertEqual(profile.organizations[0].identifiers, [])
        self.assertEqual(profile.organizations[0].phone_numbers[0].phone_number, "2125550199")
        self.assertEqual(profile.organizations[0].locations[0].address.line1, "123 Main St")
        self.assertTrue(profile.organizations[0].locations[0].is_primary_organization_location)
        self.assertEqual(profile.organizations[0].locations[0].phone_number.phone_extension, "99")

        first_sql, first_params = fetcher.calls[0]
        self.assertIn("FROM practitioner p", first_sql)
        self.assertEqual(first_params["first_name"], "jane")
        self.assertEqual(first_params["last_name"], "doe")
        self.assertEqual(first_params["date_of_birth"], date(1980, 1, 2))
        self.assertEqual(first_params["ssn"], "123456789")

    def test_lookup_returns_none_when_no_match_exists(self):
        service = PractitionerProfileService(fetch_all_fn=StubFetcher([("FROM practitioner p", [])]))

        profile = service.lookup_practitioner_profile(
            first_name="Jane",
            last_name="Doe",
            date_of_birth=date(1980, 1, 2),
            ssn="123456789",
        )

        self.assertIsNone(profile)

    def test_lookup_raises_for_ambiguous_matches(self):
        service = PractitionerProfileService(
            fetch_all_fn=StubFetcher(
                [
                    (
                        "FROM practitioner p",
                        [
                            {"practitioner_id": uuid4()},
                            {"practitioner_id": uuid4()},
                        ],
                    )
                ]
            )
        )

        with self.assertRaises(AmbiguousPractitionerMatchError):
            service.lookup_practitioner_profile(
                first_name="Jane",
                last_name="Doe",
                date_of_birth=date(1980, 1, 2),
                ssn="123456789",
            )
