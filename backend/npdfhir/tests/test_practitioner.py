from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase
from .fixtures.practitioner import (
    DefaultPractitioner,
    DefaultIndividual,
    DefaultName,
    DefaultNPI,
    DefaultOtherID,
)
from .fixtures.address import DefaultAddress
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_practitioner_names,
    get_female_npis,
    concat_address_string,
)
from ..models import ProviderView

practitioners = [{}]


class PractitionerViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Generate test data for NUCC Code filtering
        # Practitioner with the NUCC Codes 363L00000X (Nurse) and 364SP0200X (Non-nurse)
        cls.nurse_prac = DefaultPractitioner(
            taxonomies=["363L00000X", "364SP0200X"],
        )
        # Practitioner with the NUCC Code "204F00000X" (Transplant)
        cls.non_nurse_prac = DefaultPractitioner(
            taxonomies=["204F00000X"],
        )
        # Practitioner with the NUCC Code "101Y00000X" (Counselor)
        cls.non_nurse_prac = DefaultPractitioner(
            taxonomies=["101Y00000X"],
        )

        # Generate test data for alpha sorting
        cls.names_for_sorting = [
            ("AADALEN", "KIRK"),
            ("ABBAS", "ASAD"),
            ("ABBOTT", "BRUCE"),
            ("ABBOTT", "PHILIP"),
            ("ABDELHALIM", "AHMED"),
            ("ABDELHAMED", "ABDELHAMED"),
            ("ABDEL NOUR", "MAGDY"),
            ("ABEL", "MICHAEL"),
            ("ABELES", "JENNIFER"),
            ("ABELSON", "MARK"),
            ("CUTLER", "A"),
            ("NIZAM", "A"),
            ("SALAIS", "A"),
            ("JANOS", "AARON"),
            ("NOONBERG", "AARON"),
            ("PITNEY", "AARON"),
            ("SOLOMON", "AARON"),
            ("STEIN", "AARON"),
            ("ALI", "ABBAS"),
            ("JAFRI", "ABBAS"),
            ("ZWERLING", "HAYWARD"),
            ("ZUROSKE", "GLEN"),
            ("ZUCKERBERG", "EDWARD"),
            ("ZUCKER", "WILLIAM"),
            ("ZUCCALA", "SCOTT"),
            ("ZOVE", "DANIEL"),
            ("ZORN", "GUNNAR"),
            ("ZOOG", "EUGENE"),
            ("ZOLMAN", "MARK"),
            ("ZOLLER", "DAVID"),
        ]
        for name in cls.names_for_sorting:
            DefaultPractitioner(
                individual=DefaultIndividual(
                    names=[DefaultName(last_name=name[0], first_name=name[1])]
                )
            )

        # Generate test data for address filtering
        addresses = [
            {
                "city": "Springfield",
                "state": "CA",
                "zip_code": "12345",
                "line_1": "113 Stadium Blvd.",
            },
            {
                "city": "Sacramento",
                "state": "CA",
                "zip_code": "04321",
                "line_1": "333 Rocky Road.",
            },
            {
                "city": "Rochester",
                "state": "NY",
                "zip_code": "33333",
                "line_1": "123 Street R.",
            },
        ]
        for address in addresses:
            DefaultPractitioner(individual=DefaultIndividual(addresses=[DefaultAddress(**address)]))

        # Generate test data for an address that is a home address
        DefaultPractitioner(
            individual=DefaultIndividual(addresses=[DefaultAddress(address_use_id=1)])
        )

        # Generate test data for gender filtering
        DefaultPractitioner(individual=DefaultIndividual(gender="M"))

        # Generate test data for NPI filtering
        DefaultPractitioner(
            individual=DefaultIndividual(id="5d0ef58e-0dab-4274-902f-387f61f7c76d"),
            npi=DefaultNPI(npi=1234567890),
        )

        # Generate test data for other identifier filtering
        DefaultPractitioner(
            individual=DefaultIndividual(id="eef22b6f-4548-44fb-9d96-69328df19810"),
            other_ids=[DefaultOtherID(other_id=1234567890)],
        )

        # Generate test data for retrieving specific Practitioner
        DefaultPractitioner(individual=DefaultIndividual(id="6c6a26af-9d9d-447f-b03f-22bda49675c6"))

        ProviderView.refresh_materialized_view()

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-practitioner-list")  # /Practitioner/
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        sorted_names = self.names_for_sorting[0:10]
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # Extract names
        names = extract_practitioner_names(response)

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir practitioners sorted by family then first name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_alternate_order(self):
        sorted_names = self.names_for_sorting[10:20]
        url = reverse("fhir-practitioner-list")
        response = self.client.get(
            url,
            {"_sort": "first_name,last_name"},
        )
        assert_fhir_response(self, response)

        # Extract names
        names = extract_practitioner_names(response)

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir practitioners sorted by first then family name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_descending_order(self):
        sorted_names = self.names_for_sorting[20:]
        url = reverse("fhir-practitioner-list")
        response = self.client.get(
            url,
            {"_sort": "-last_name,-first_name"},
        )
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_practitioner_names(response)

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir practitioners sorted by family then first name in descending but got {names}\n Sorted: {sorted_names}",
        )

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Basic Filter tests
    def test_list_filter_by_gender(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"gender": "Male"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Assert all required fields are present to get npi id
        assert_has_results(self, response)
        self.assertIn("entry", response.data["results"])

        npi_ids = []
        for practitioner_entry in response.data["results"]["entry"]:
            self.assertIn("resource", practitioner_entry)
            self.assertIn("id", practitioner_entry["resource"])
            npi_id = practitioner_entry["resource"]["identifier"][0]["value"]
            npi_ids.append(int(npi_id))

        # Check to make sure no female practitioners were fetched by mistake
        should_be_empty = get_female_npis(npi_ids)
        self.assertFalse(should_be_empty)

    def test_list_filter_by_name(self):
        test_name = "Solomon"
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"name": test_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            names = []
            for name in entry["resource"]["name"]:
                names.append(name["family"])
                names += name["given"]

            self.assertIn(test_name.upper(), names)

    def test_list_filter_by_practitioner_type(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"practitioner_type": "Nurse"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            nurse_codes = [
                nc["code"] for nc in entry["resource"]["qualification"][0]["code"]["coding"]
            ]
            self.assertIn("363L00000X", nurse_codes)
            self.assertNotIn("204F00000X", nurse_codes)

    # Identifiers Filter tests
    def test_list_filter_by_identifier_general(self):
        identifier = "1234567890"

        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": identifier})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        ids = []
        for entry in response.data["results"]["entry"]:
            ids.append(entry["resource"]["id"])
            values = [str(v["value"]) for v in entry["resource"]["identifier"]]
            self.assertIn(str(identifier), values)

        # assert that the Practitioner with the npi 1234567890 is present
        self.assertIn("5d0ef58e-0dab-4274-902f-387f61f7c76d", ids)
        # assert that the Practitioner with the other identifier 1234567890 is present
        self.assertIn("eef22b6f-4548-44fb-9d96-69328df19810", ids)

    def test_list_filter_by_npi_specific(self):
        npi = "1234567890"
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": f"NPI|{npi}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        ids = []
        for entry in response.data["results"]["entry"]:
            ids.append(entry["resource"]["id"])
            values = [str(v["value"]) for v in entry["resource"]["identifier"]]
            self.assertIn(npi, values)

        # assert that the Practitioner with the npi 1234567890 is present
        self.assertIn("5d0ef58e-0dab-4274-902f-387f61f7c76d", ids)
        # assert that the Practitioner with the other identifier 1234567890 is not present
        self.assertNotIn("eef22b6f-4548-44fb-9d96-69328df19810", ids)

    # Address Filter tests
    def test_list_filter_by_address(self):
        url = reverse("fhir-practitioner-list")
        test_search = "123 Street R. Rochester"
        response = self.client.get(url, {"address": test_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            present_checks = []
            for address in entry["resource"]["address"]:
                address_string = concat_address_string(address)
                present_checks.append(test_search in address_string)
            self.assertTrue(any(present_checks))

    def test_list_filter_by_address_leading_zero(self):
        url = reverse("fhir-practitioner-list")
        test_search = "333 Rocky Road. Sacramento 04321"
        response = self.client.get(url, {"address": test_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            present_checks = []
            for address in entry["resource"]["address"]:
                address_string = concat_address_string(address)
                if "333 Rocky Road. Sacramento" in address_string and "04321" in address_string:
                    present_checks.append(True)
            self.assertTrue(any(present_checks))

    def test_list_filter_by_address_city(self):
        url = reverse("fhir-practitioner-list")
        city_string = "Springfield"
        response = self.client.get(url, {"address_city": city_string})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            cities = []
            for address in entry["resource"]["address"]:
                cities.append(address["city"])

            self.assertIn(city_string, cities)

    def test_list_filter_by_address_state(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"address_state": "CA"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        state_abreviations = [
            d["resource"]["address"][0]["state"] for d in response.data["results"]["entry"]
        ]

        for state in state_abreviations:
            self.assertEqual("CA", state)

    def test_list_filter_by_address_postalcode(self):
        url = reverse("fhir-practitioner-list")
        postal_code_string = "12345"
        response = self.client.get(url, {"address_postalcode": postal_code_string})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            zips = []
            for address in entry["resource"]["address"]:
                zips.append(address["postalCode"])
            self.assertIn(postal_code_string, zips)

    def test_list_filter_by_address_postalcode_leading_zero(self):
        url = reverse("fhir-practitioner-list")
        postal_code_string = "04321"
        response = self.client.get(url, {"address_postalcode": postal_code_string})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            zips = []
            for address in entry["resource"]["address"]:
                zips.append(address["postalCode"])
            self.assertIn(postal_code_string, zips)

    def test_list_filter_by_address_use(self):
        url = reverse("fhir-practitioner-list")

        response = self.client.get(url, {"address_use": "home"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            uses = []
            for address in entry["resource"]["address"]:
                # assert the address use is in the data
                self.assertIn("use", address)
                uses.append(address["use"])
            self.assertIn("home", uses)

    # Retrieve tests
    def test_retrieve_nonexistent(self):
        url = reverse("fhir-practitioner-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-practitioner-detail", args=["12300000-0000-0000-0000-000000000123"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_pracitioner(self):
        id = "6c6a26af-9d9d-447f-b03f-22bda49675c6"
        url = reverse("fhir-practitioner-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))
