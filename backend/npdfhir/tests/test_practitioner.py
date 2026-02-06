from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase
from .fixtures.location import create_location
from .fixtures.practitioner import create_practitioner
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_practitioner_names,
    get_female_npis,
    concat_address_string
)


class PractitionerViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.locs = [
            create_location(
                name="California Location A",
                city="Springfield",
                state="CA",
                zipcode="12345",
                addr_line_1="113 Stadium Blvd.",
            ),
            create_location(
                name="California Location B",
                city="Sacramento",
                state="CA",
                zipcode="54321",
                addr_line_1="333 Rocky Road.",
            ),
            create_location(
                name="New York Location A",
                city="Rochester",
                state="NY",
                zipcode="33333",
                addr_line_1="123 Street R.",
            ),
        ]

        cls.nurse_code = "363L00000X"
        cls.non_nurse_code = "364SP0200X"
        cls.nurse_prac = create_practitioner(
            last_name="ZOLLER",
            first_name="DAVID",
            practitioner_types=[cls.nurse_code, cls.non_nurse_code],
        )

        cls.transplant_code = "204F00000X"
        cls.non_nurse_prac = create_practitioner(
            last_name="MILLER",
            first_name="STACY",
            practitioner_types=[cls.transplant_code],
        )

        cls.counselor = "101Y00000X"
        cls.non_nurse_prac = create_practitioner(
            last_name="TROY",
            first_name="DIANA",
            practitioner_types=[cls.counselor],
        )

        cls.sample_last_name = "SOLOMON"
        cls.pracs = [
            create_practitioner(last_name="AADALEN", first_name="KIRK", npi_value=1234567890),
            create_practitioner(last_name="ABBAS", first_name="ASAD", other_id=1234567890),
            create_practitioner(last_name="ABBOTT", first_name="BRUCE"),
            create_practitioner(last_name="ABBOTT", first_name="PHILIP"),
            create_practitioner(last_name="ABDELHALIM", first_name="AHMED"),
            create_practitioner(last_name="ABDELHAMED", first_name="ABDELHAMED"),
            create_practitioner(last_name="ABDEL NOUR", first_name="MAGDY"),
            create_practitioner(last_name="ABEL", first_name="MICHAEL", location=cls.locs[0]),
            create_practitioner(last_name="ABELES", first_name="JENNIFER"),
            create_practitioner(last_name="ABELSON", first_name="MARK", location=cls.locs[2]),
            create_practitioner(last_name="CUTLER", first_name="A"),
            create_practitioner(last_name="NIZAM", first_name="A"),
            create_practitioner(last_name="SALAIS", first_name="A"),
            create_practitioner(
                last_name="JANOS", first_name="AARON", location=cls.locs[1], address_use="home"
            ),
            create_practitioner(last_name="NOONBERG", first_name="AARON"),
            create_practitioner(last_name="PITNEY", first_name="AARON"),
            create_practitioner(last_name=cls.sample_last_name, first_name="AARON"),
            create_practitioner(last_name="STEIN", first_name="AARON"),
            create_practitioner(last_name="ALI", first_name="ABBAS"),
            create_practitioner(last_name="JAFRI", first_name="ABBAS"),
            create_practitioner(last_name="ZWERLING", first_name="HAYWARD"),
            create_practitioner(last_name="ZUROSKE", first_name="GLEN"),
            create_practitioner(last_name="ZUCKERBERG", first_name="EDWARD"),
            create_practitioner(last_name="ZUCKER", first_name="WILLIAM"),
            create_practitioner(last_name="ZUCCALA", first_name="SCOTT", gender="M"),
            create_practitioner(last_name="ZOVE", first_name="DANIEL"),
            create_practitioner(last_name="ZORN", first_name="GUNNAR"),
            create_practitioner(last_name="ZOOG", first_name="EUGENE"),
            create_practitioner(last_name="ZOLMAN", first_name="MARK"),
            cls.nurse_prac,
        ]

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-practitioner-list")  # /Practitioner/
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'][0])

        # for name in response.data["results"]["entry"]:
        #    print(name['resource']['name'][-1])

        # Extract names
        names = extract_practitioner_names(response)

        sorted_names = [
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
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir practitioners sorted by family then first name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_alternate_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(
            url,
            {
                "_sort": "individual__individualtoname__first_name,individual__individualtoname__last_name"
            },
        )
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'][0])

        # for name in response.data["results"]["entry"]:
        #    print(name['resource']['name'][-1])

        # Extract names
        names = extract_practitioner_names(response)

        sorted_names = [
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
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir practitioners sorted by first then family name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_descending_order(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(
            url,
            {
                "_sort": "-individual__individualtoname__last_name,-individual__individualtoname__first_name"
            },
        )
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_practitioner_names(response)

        sorted_names = [
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
            npi_id = practitioner_entry["resource"]['identifier'][0]['value']
            npi_ids.append(int(npi_id))

        # Check to make sure no female practitioners were fetched by mistake
        should_be_empty = get_female_npis(npi_ids)
        self.assertFalse(should_be_empty)

    def test_list_filter_by_name(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"name": self.sample_last_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            names = []
            for name in entry["resource"]["name"]:
                names.append(name["family"])
                names.append(name["given"])

            self.assertIn(self.sample_last_name, names)

    def test_list_filter_by_practitioner_type(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"practitioner_type": "Nurse"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            nurse_codes = [
                nc["code"] for nc in entry["resource"]["qualification"][0]["code"]["coding"]
            ]
            self.assertIn(self.nurse_code, nurse_codes)
            self.assertNotIn(self.transplant_code, nurse_codes)

    # Identifiers Filter tests
    def test_list_filter_by_identifier_general(self):
        identifier = "1234567890"

        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": identifier})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        all_values = []
        for entry in response.data["results"]["entry"]:
            values = [int(v["value"]) for v in entry["resource"]["identifier"]]
            all_values.extend(values)
            self.assertIn(int(identifier), values)

        # assert that Kirk Aadalen is in the data
        self.assertIn(self.pracs[0].npi.npi, all_values)
        # assert that Asad Abbas is in the data
        self.assertIn(self.pracs[1].npi.npi, all_values)

    def test_list_filter_by_npi_specific(self):
        url = reverse("fhir-practitioner-list")
        response = self.client.get(url, {"identifier": "NPI|1234567890"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            values = [int(v["value"]) for v in entry["resource"]["identifier"]]
            self.assertIn(self.pracs[0].npi.npi, values)

        self.assertEqual(len(response.data["results"]["entry"]), 1)

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
                # print(address)
                address_string = concat_address_string(address)

                # self.assertIn(test_search, address_string)
                present_checks.append(test_search in address_string)
            self.assertTrue(any(present_checks))

    def test_list_filter_by_address_city(self):
        url = reverse("fhir-practitioner-list")
        city_string = self.locs[0].address.address_us.city_name
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
        postal_code_string = self.locs[0].address.address_us.zipcode
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
        id = self.pracs[0].individual.id
        url = reverse("fhir-practitioner-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))
