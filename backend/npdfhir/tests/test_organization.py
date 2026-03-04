from django.urls import reverse
from rest_framework import status

from ..models import Organization, OrganizationView
from .api_test_case import APITestCase
from .fixtures.organization import DefaultOrganization, DefaultLocation
from .fixtures.practitioner import DefaultOtherID, DefaultNPI
from .fixtures.address import DefaultAddress
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
        # Generate test data to test sorting
        cls.names_for_sorting = [
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
            "ZUNI HOME HEALTH CARE AGENCY",
            "ZEELAND COMMUNITY HOSPITAL",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNG C. BAE, M.D.",
            "YORKTOWN EMERGENCY MEDICAL SERVICE",
            "YODORINCMISSIONPLAZAPHARMACY",
            "YOAKUM COMMUNITY HOSPITAL",
        ]
        for name in cls.names_for_sorting:
            DefaultOrganization(names=[name])

        # Generate test data for an organization with an alias
        DefaultOrganization(names=["YARMOUTH AUDIOLOGY", "ABC YARMOUTH"])

        # Generate test data for organization hierarchies
        DefaultOrganization(names=["Parent Org"], id="c591bfc5-b4ed-49af-926f-569056b5b1aa")
        DefaultOrganization(
            names=["Child Org"],
            id="5f56f3f0-3bd6-42ce-b275-f12f92a4ba40",
            parent_id="c591bfc5-b4ed-49af-926f-569056b5b1aa",
        )

        # Generate test data for a non-clinical organization
        DefaultOrganization(
            id="f3aa2e21-6163-4f56-b6d2-259ff009c607",
            names=["Joe Health Incorporated"],
            is_clinical=False,
        )

        # Generate test data for organizations with various locations
        locations = [
            {
                "city": "Boston",
                "state": "MA",
                "zip_code": "10001",
                "line_1": "1 Boston Avenue",
            },
            {
                "city": "Sandiego",
                "state": "CA",
                "zip_code": "05555",
                "line_1": "404 Great Amazing Avenue",
            },
            {
                "state": "NY",
            },
        ]
        for location in locations:
            DefaultOrganization(locations=[DefaultLocation(address=DefaultAddress(**location))])

        # Generate test data for locations with an other ids
        DefaultOrganization(other_ids=[DefaultOtherID(other_id="testMBI")])

        # Generate test data for an organization with a different NUCC code (283Q00000X - Psychiatric Hospital)
        DefaultOrganization(id="cc9d6beb-992f-47f6-8f41-a10d4cf13694", taxonomies=["283Q00000X"])

        # Generate test data for an organization with a custom NPI
        DefaultOrganization(npi=DefaultNPI(npi=1427051473))

        # Generate test data for retrieving a specific Organization
        DefaultOrganization(id="5fe868ad-2d9e-467e-b208-b0cfcfa39054")

        OrganizationView.refresh_materialized_view()

        return super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.org_without_authorized_official = Organization.objects.create(
            id="26708690-19d6-499e-b481-cebe05b98f08",
            authorized_official_id=None,
        )
        OrganizationView.refresh_materialized_view()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

        bundle = response.data["results"]

        # Assert each entry has basic keys
        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]

            self.assertEqual(org_entry["resourceType"], "Organization")
            self.assertIn("identifier", org_entry)
            self.assertIn("meta", org_entry)
            self.assertIn("name", org_entry)
            self.assertIn("contact", org_entry)

    def test_taxonomy_extensions(self):
        id = "5fe868ad-2d9e-467e-b208-b0cfcfa39054"

        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        org = response.data
        self.assertEqual(org["resourceType"], "Organization")
        self.assertEqual(org["name"], "Organization ABC")

        org_type_extension = org["extension"][0]

        self.assertIn("valueCodeableConcept", org_type_extension)
        self.assertIn("url", org_type_extension)
        extension_url = (
            "https://build.fhir.org/organization-definitions.html#Organization.qualification"
        )
        self.assertEqual(org_type_extension["url"], extension_url)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # Extract names
        names = extract_resource_names(response)

        sorted_names = self.names_for_sorting[0:10]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir orgs sorted by org name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_descending_order(self):
        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"_sort": "-name"})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        sorted_names = [{}] + self.names_for_sorting[-7:] + ["YARMOUTH AUDIOLOGY", "Parent Org"]

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
    def test_list_filter_by_nonexistent_name(self):
        filter_param_value = "Cumberland"

        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": filter_param_value})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertEqual(0, response.data["count"])

        self.assertEqual([], response.data["results"]["entry"])

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

    def test_list_filter_by_y_name(self):
        y_name = "SUPPLY"

        url = reverse("fhir-organization-list")
        response = self.client.get(url, {"name": y_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)

            org_entry = entry["resource"]
            names = org_entry["name"]
            if "alias" in org_entry.keys():
                names += org_entry["alias"]

            self.assertIn(y_name, names)

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
            nucc_display_name = org_entry["extension"][0]["valueCodeableConcept"]["coding"][0][
                "display"
            ]

            self.assertIn(filter_param_value, nucc_display_name)
            self.assertEqual("cc9d6beb-992f-47f6-8f41-a10d4cf13694", org_entry["id"])

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
        parent_id = "c591bfc5-b4ed-49af-926f-569056b5b1aa"
        id = "5f56f3f0-3bd6-42ce-b275-f12f92a4ba40"
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
        id = "f3aa2e21-6163-4f56-b6d2-259ff009c607"

        url = reverse("fhir-organization-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        org = response.data
        self.assertEqual(org["resourceType"], "Organization")
        self.assertEqual(org["name"], "Joe Health Incorporated")

    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-organization-detail", args=["12300000-0000-0000-0000-000000000123"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_npi(self):
        url = reverse("fhir-organization-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_organization(self):
        id = "5fe868ad-2d9e-467e-b208-b0cfcfa39054"
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
