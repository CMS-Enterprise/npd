from django.urls import reverse
from rest_framework import status

from ..models import Organization, OtherIdType
from .api_test_case import APITestCase
from .fixtures.organization import create_legal_entity, create_organization
from .fixtures.location import create_location
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
    concat_address_string,
)


class OrganizationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.orgs = [
            create_organization(
                name="1ST CHOICE HOME HEALTH CARE INC", id="c591bfc5-b4ed-49af-926f-569056b5b1aa"
            ),
            create_organization(
                name="1ST CHOICE MEDICAL DISTRIBUTORS, LLC",
                id="5f56f3f0-3bd6-42ce-b275-f12f92a4ba40",
                parent_id="c591bfc5-b4ed-49af-926f-569056b5b1aa",
            ),
            create_organization(
                name="986 INFUSION PHARMACY #1 INC.", aliases=["INFUSION INC.", "ABC Infusion"]
            ),
            create_organization(name="A & A MEDICAL SUPPLY COMPANY"),
            create_organization(name="ABACUS BUSINESS CORPORATION GROUP INC."),
            create_organization(name="ABBY D CENTER, INC."),
            create_organization(name="ABC DURABLE MEDICAL EQUIPMENT INC"),
            create_organization(name="ABC HOME MEDICAL SUPPLY, INC."),
            create_organization(name="A BEAUTIFUL SMILE DENTISTRY, L.L.C."),
            create_organization(name="A & B HEALTH CARE, INC."),
            create_organization(name="ZUNI HOME HEALTH CARE AGENCY"),
            create_organization(name="ZEELAND COMMUNITY HOSPITAL"),
            create_organization(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD"),
            create_organization(name="YOUNG C. BAE, M.D."),
            create_organization(name="YORKTOWN EMERGENCY MEDICAL SERVICE"),
            create_organization(name="YODORINCMISSIONPLAZAPHARMACY"),
            create_organization(name="YOAKUM COMMUNITY HOSPITAL"),
            create_organization(name="YARMOUTH AUDIOLOGY", aliases=["ABC YARMOUTH"]),
        ]

        cls.locs = [
            create_location(name="Main Clinic", organization=cls.orgs[0]),
            create_location(name="1ST CHOICE MEDICAL DISTRIBUTORS, LLC", organization=cls.orgs[0]),
            create_location(name="986 INFUSION PHARMACY #1 INC.", organization=cls.orgs[1]),
            create_location(
                name="A & A MEDICAL SUPPLY COMPANY",
                organization=cls.orgs[2],
                city="Boston",
                state="MA",
                zipcode="10001",
                addr_line_1="1 Boston Avenue",
            ),
            create_location(
                name="ABACUS BUSINESS CORPORATION GROUP INC.",
                organization=cls.orgs[3],
                city="Sandiego",
                state="CA",
                zipcode="05555",
                addr_line_1="404 Great Amazing Avenue",
            ),
        ]

        cls.joe_legal_entity = create_legal_entity(dba_name="Joe Administrative Services LLC")
        cls.joe_name = "Joe Health Incorporated"
        cls.joe_health_org = create_organization(
            name=cls.joe_name, legal_entity=cls.joe_legal_entity
        )
        cls.orgs.append(cls.joe_health_org)

        cls.other_id = OtherIdType.objects.first()
        cls.other_id_org = create_organization(name="Beaver Clinicals", other_id_type=cls.other_id)
        cls.orgs.append(cls.other_id_org)

        cls.hospital_nucc_org = create_organization(
            name="TestNuccOrg", organization_type="283Q00000X"
        )
        cls.orgs.append(cls.hospital_nucc_org)

        cls.org_with_npi = create_organization(name="Custom NPI General", npi_value=1427051473)
        cls.orgs.append(cls.org_with_npi)

        cls.org_cumberland = create_organization(name="Cumberland")
        cls.orgs.append(cls.org_cumberland)

        return super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.org_without_authorized_official = Organization.objects.create(
            id="26708690-19d6-499e-b481-cebe05b98f08", authorized_official_id=None
        )

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # print(response.data["results"]["entry"][0]['resource']['name'])

        # Extract names
        names = extract_resource_names(response)

        sorted_names = [
            "1ST CHOICE HOME HEALTH CARE INC",
            "1ST CHOICE MEDICAL DISTRIBUTORS, LLC",
            "986 INFUSION PHARMACY #1 INC.",
            "A & A MEDICAL SUPPLY COMPANY",
            "ABACUS BUSINESS CORPORATION GROUP INC.",
            "ABBY D CENTER, INC.",
            "ABC DURABLE MEDICAL EQUIPMENT INC",
            "ABC HOME MEDICAL SUPPLY, INC.",
            "A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
            "A & B HEALTH CARE, INC.",
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir orgs sorted by org name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_descending_order(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"_sort": "-primary_name"})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        sorted_names = [
            {},
            "ZUNI HOME HEALTH CARE AGENCY",
            "ZEELAND COMMUNITY HOSPITAL",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNG C. BAE, M.D.",
            "YORKTOWN EMERGENCY MEDICAL SERVICE",
            "YODORINCMISSIONPLAZAPHARMACY",
            "YOAKUM COMMUNITY HOSPITAL",
            "YARMOUTH AUDIOLOGY",
            "TestNuccOrg",
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir org list sorted descending by name but got {names}\n Sorted: {sorted_names}",
        )

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Basic Filter tests
    def test_list_filter_by_name(self):
        filter_param_value = "Cumberland"

        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]
            param_in_name = [filter_param_value in org_entry["name"]]

            if "alias" in org_entry:
                for n in org_entry["alias"]:
                    param_in_name.append(filter_param_value in n)

            self.assertTrue(any(param_in_name))

    def test_list_filter_by_name_broad(self):
        filter_param_value = "ABC"
        ensure_in_results = ["ABC HOME MEDICAL SUPPLY, INC.", "ABC DURABLE MEDICAL EQUIPMENT INC"]

        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for ensure_name in ensure_in_results:
            names = [entry["resource"]["name"] for entry in bundle["entry"]]

            for entry in bundle["entry"]:
                if "alias" in entry["resource"]:
                    names.extend(alias for alias in entry["resource"]["alias"])

            self.assertIn(ensure_name, names)

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]
            param_in_name = [filter_param_value in org_entry["name"]]

            if "alias" in org_entry:
                for n in org_entry["alias"]:
                    param_in_name.append(filter_param_value in n)

            self.assertTrue(any(param_in_name))

    def test_list_filter_by_name_specific(self):
        filter_param_value = "ABC HOME MEDICAL SUPPLY, INC."
        ensure_not_in_results = "ABC DURABLE MEDICAL EQUIPMENT INC"

        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]
            param_in_name = [filter_param_value in org_entry["name"]]

            if "alias" in org_entry:
                for n in org_entry["alias"]:
                    param_in_name.append(filter_param_value in n)
                    self.assertNotIn(ensure_not_in_results, n)

            self.assertTrue(any(param_in_name))
            self.assertNotIn(ensure_not_in_results, org_entry["name"])

    def test_list_filter_by_organization_type(self):
        filter_param_value = "Hospital"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"organization_type": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]

            self.assertEqual(org_entry["id"], str(self.hospital_nucc_org.id))

    # Identifiers Filter tests
    def test_list_filter_by_npi_general(self):
        filter_param_value = "1427051473"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"identifier": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]

            identifiers = [identifier["value"] for identifier in org_entry["identifier"]]

            self.assertIn(filter_param_value, identifiers)

    def test_list_filter_by_npi_specific(self):
        filter_param_value = "1427051473"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"identifier": f"NPI|{filter_param_value}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]

            identifiers = [
                identifier
                for identifier in org_entry["identifier"]
                if filter_param_value in identifier["value"]
            ]

            self.assertTrue(identifiers)

            for identifier in identifiers:
                self.assertIn("http://terminology.hl7.org/NamingSystem/npi", identifier["system"])

    def test_parent_id(self):
        parent_id = self.orgs[1].parent_id
        id = self.orgs[1].id
        url = reverse("fhir-organization-detail", args=[parent_id])
        response = self.client.get(url)
        # check that the parentless organization does not have a parent listed
        self.assertNotIn("partOf", str(response.data.keys()))

        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        # check that the child organization has a parent_id listed
        self.assertIn("partOf", str(response.data.keys()))
        # check that the child organization has the correct parent_id listed
        self.assertIn(parent_id, f"Organization/{response.data['partOf']['reference']}")

    def test_list_filter_by_otherID_general(self):
        filter_param_value = "testMBI"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"identifier": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]
            identifiers = [identifier["value"] for identifier in org_entry["identifier"]]

            self.assertIn(filter_param_value, identifiers)

    # def test_list_filter_by_otherID_specific(self):
    #     url = reverse("fhir-organization-list")
    #     response = self.client.get(url, {"identifier":"	1|001586989"})
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     assert_has_results(self, response)
    #     self.assertGreaterEqual(response.data["results"]["total"], 1)

    # Address Filter tests
    def test_list_filter_by_address(self):
        address_search = "Main"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                address_string = concat_address_string(address["address"])
                search_in_location_list.append(address_search in address_string)

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_zipcode_leading_zero(self):
        address_search = "404 Great Amazing Avenue Sandiego CA 05555"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                address_string = concat_address_string(address["address"])
                search_in_location_list.append(address_search in address_string)

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_city(self):
        address_search = "Boston"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address_city": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                search_in_location_list.append(address_search in address["address"]["city"])

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_state(self):
        address_search = "NY"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address_state": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                search_in_location_list.append(address_search == address["address"]["state"])

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_postalcode(self):
        address_search = "10001"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address_postalcode": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                search_in_location_list.append(address_search in address["address"]["postalCode"])

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_zipcode_filter_leading_zero(self):
        address_search = "05555"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address_postalcode": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                search_in_location_list.append(address_search in address["address"]["postalCode"])

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    def test_list_filter_by_address_use(self):
        address_search = "work"
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"address_use": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertIn("id", location_entry)
            self.assertIn("contact", location_entry)
            # self.assertIn("name", location_entry)

            search_in_location_list = []

            for address in location_entry["contact"]:
                self.assertIn("address", address)
                search_in_location_list.append(address_search in address["address"]["use"])

            self.assertTrue(any(search_in_location_list))

            self.assertEqual(location_entry["resourceType"], "Organization")

    # Retrieve tests
    def test_retrieve_non_clinical_organization(self):
        id = self.joe_health_org.id

        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        org = response.data
        self.assertEqual(org["resourceType"], "Organization")
        self.assertEqual(org["name"], self.joe_name)

    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-organization-detail", args=["12300000-0000-0000-0000-000000000123"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_npi(self):
        url = reverse("fhir-organization-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_organization(self):
        id = self.orgs[0].id
        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))

    # Edge cases tests
    def test_organization_without_authorized_official(self):
        id = self.org_without_authorized_official.pk
        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], id)
