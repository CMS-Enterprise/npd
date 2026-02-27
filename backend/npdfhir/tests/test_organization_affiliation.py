from django.urls import reverse
from rest_framework import status
from .api_test_case import APITestCase
from .fixtures.endpoint import DefaultEhrVendor, DefaultEndpointInstance
from .fixtures.organization import DefaultOrganization, DefaultLocation
from .fixtures.organization import DefaultAddress
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    extract_resource_ids,
    extract_resource_fields,
)


class OrganizationAffiliationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        """
        Creates a mix of organizations:
        - Some that SHOULD match the query
        - Some that SHOULD NOT match the query
        """
        cls.orgs = []

        # Generate test data for an organization that has a single endpoint associated with default ehr vendor
        org = DefaultOrganization(
            names=["A Good Clinical Org"],
            id="a9cd57b1-9e8c-4b75-86da-653acfc3ade6",
            taxonomies=["283Q00000X"],
            locations=[
                DefaultLocation(
                    name="Good Location 1",
                    address=DefaultAddress(zip_code="87101"),
                    endpoint_instance=DefaultEndpointInstance(
                        name="Good Endpoint 1",
                        ehr_vendor=DefaultEhrVendor(name="Vendor of EHR Systems"),
                    ),
                )
            ],
        )
        cls.orgs.append(org)

        # Generate test data for an organization with multiple endpoints, same EHR vendor
        org = DefaultOrganization(
            names=["B Good Clinical Org"],
            locations=[
                DefaultLocation(
                    name="Location A",
                    address=DefaultAddress(
                        line_1="807 Dusty Ln", city="Springfield", state="NY", zip_code="01234"
                    ),
                    endpoint_instance=DefaultEndpointInstance(name="Endpoint A"),
                ),
                DefaultLocation(
                    name="Location B",
                    endpoint_instance=DefaultEndpointInstance(name="Endpoint B"),
                ),
            ],
        )
        cls.orgs.append(org)

        # Generate test data for an organization with multiple endpoints, different EHR vendors
        org = DefaultOrganization(
            names=["C Good Clinical Org"],
            locations=[
                DefaultLocation(
                    name="Location A",
                    endpoint_instance=DefaultEndpointInstance(
                        name="Endpoint A", ehr_vendor=DefaultEhrVendor(name="EHR Vendor A")
                    ),
                ),
                DefaultLocation(
                    name="Location B",
                    endpoint_instance=DefaultEndpointInstance(
                        name="Endpoint B", ehr_vendor=DefaultEhrVendor(name="EHR Vendor B")
                    ),
                ),
            ],
        )
        cls.orgs.append(org)

        # Generate test data for an organization with no location
        cls.org_with_no_location = DefaultOrganization(
            names=["No Location Org"], has_locations=False
        )

        # Generate test data for an organization with a location, but no endpoint
        cls.org_with_no_affiliation = DefaultOrganization(
            names=["No Endpoint Org"], locations=[DefaultLocation(has_endpoint=False)]
        )

        # Generate test data for an EHR Vendor that has no organizations associated
        DefaultEhrVendor(name="Lonely EHR Vendor")

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            org_affiliation_entry = entry["resource"]
            self.assertEqual(org_affiliation_entry["resourceType"], "OrganizationAffiliation")

            self.assertIn("id", org_affiliation_entry)
            self.assertIn("organization", org_affiliation_entry)
            self.assertIn("participatingOrganization", org_affiliation_entry)
            self.assertIn("endpoint", org_affiliation_entry)

    def test_list_in_default_order(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        particpiationg_orgs = extract_resource_fields(response, "participatingOrganization")
        participating_org_names = [org["display"] for org in particpiationg_orgs]

        sorted = ["A Good Clinical Org", "B Good Clinical Org", "C Good Clinical Org"]

        self.assertEqual(
            participating_org_names,
            sorted,
            f"Expected fhir org affilations sorted by participating org name but got {participating_org_names}\n Sorted: {sorted}",
        )

    def test_list_in_descending_order(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"_sort": "-organization_name"})
        assert_fhir_response(self, response)

        particpiationg_orgs = extract_resource_fields(response, "participatingOrganization")
        participating_org_names = [org["display"] for org in particpiationg_orgs]

        sorted = ["C Good Clinical Org", "B Good Clinical Org", "A Good Clinical Org"]

        self.assertEqual(
            participating_org_names,
            sorted,
            f"Expected fhir org affilations sorted in descending order by participating org name but got {participating_org_names}\n Sorted: {sorted}",
        )

    def test_list_in_ehr_vendor_order(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"_sort": "ehr_vendor_name"})
        assert_fhir_response(self, response)

        ehr_orgs = extract_resource_fields(response, "organization")
        ehr_org_names = [org["display"] for org in ehr_orgs]

        sorted = ["EHR Vendor", "EHR Vendor A", "Vendor of EHR Systems"]

        self.assertEqual(
            ehr_org_names,
            sorted,
            f"Expected fhir org affilations sorted in descending order by ehr org name but got {ehr_org_names}\n Sorted: {sorted}",
        )

    def test_list_has_correct_orgs(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)
        assert_has_results(self, response)

        ids = extract_resource_ids(response)
        ids.sort()

        valid_ids = [str(org.id) for org in self.orgs]
        valid_ids.sort()

        self.assertEqual(sorted(ids), sorted(valid_ids))

    def test_list_does_not_have_incorrect_orgs(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)
        ids = extract_resource_ids(response)

        self.assertNotIn(str(self.org_with_no_affiliation.id), ids)
        self.assertNotIn(str(self.org_with_no_location.id), ids)

    def test_org_name_filter(self):
        name_search = "Vendor of EHR Systems"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"org_name": name_search})
        bundle = response.data["results"]
        assert_has_results(self, response)

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            org_affil = entry["resource"]
            self.assertIn("id", org_affil)

            entry_org_name = org_affil["organization"]["display"]
            self.assertIn(name_search, entry_org_name)

    def test_participating_org_name_filter(self):
        name_search = "A Good Clinical Org"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"participating_org_name": name_search})
        bundle = response.data["results"]
        assert_has_results(self, response)

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            org_affil = entry["resource"]
            self.assertIn("id", org_affil)

            entry_org_name = org_affil["participatingOrganization"]["display"]
            self.assertIn(name_search, entry_org_name)

    def test_ehr_vendor_with_no_orgs(self):
        name_search = "Lonely EHR Vendor"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"participating_org_name": name_search})
        bundle = response.data["results"]

        self.assertEqual(0, len(bundle["entry"]))

    def test_org_type_filter(self):
        org_type_search = "Hospital"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"participating_organization_type": org_type_search})
        bundle = response.data["results"]
        assert_has_results(self, response)

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            org_affil = entry["resource"]
            self.assertIn("id", org_affil)

            entry_org_id = org_affil["participatingOrganization"]["reference"].split("/")[-1]
            self.assertEqual("a9cd57b1-9e8c-4b75-86da-653acfc3ade6", entry_org_id)

    def test_retrieve_single_organization_affil(self):
        id = "a9cd57b1-9e8c-4b75-86da-653acfc3ade6"
        url = reverse("fhir-organizationaffiliation-detail", args=[id])
        response = self.client.get(url)

        self.assertEqual(id, response.data["id"])

        org_affiliation_entry = response.data

        self.assertEqual(org_affiliation_entry["resourceType"], "OrganizationAffiliation")

        self.assertIn("id", org_affiliation_entry)
        self.assertIn("organization", org_affiliation_entry)
        self.assertIn("participatingOrganization", org_affiliation_entry)
        self.assertIn("endpoint", org_affiliation_entry)

    def test_list_filter_by_address(self):
        address_search = "807 Dusty Ln"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            address_lines = []
            for location in location_entry["location"]:
                returned_location = self.client.get(location["reference"]).json()
                address_lines.append(returned_location["address"])

            self.assertIn(address_search, str(address_lines))

    def test_list_filter_by_address_city(self):
        city_search = "Springfield"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"address_city": city_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            cities = []
            for location in location_entry["location"]:
                returned_location = self.client.get(location["reference"]).json()
                cities.append(returned_location["address"]["city"])

            self.assertIn(city_search, cities)

    def test_list_filter_by_address_state(self):
        state_search = "NY"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"address_state": state_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            states = []
            for location in location_entry["location"]:
                returned_location = self.client.get(location["reference"]).json()
                states.append(returned_location["address"]["state"])

    def test_list_filter_by_address_zipcode(self):
        zip_code_search = "87101"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"address_postalcode": zip_code_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            zip_codes = []
            for location in location_entry["location"]:
                returned_location = self.client.get(location["reference"]).json()
                zip_codes.append(returned_location["address"]["postalCode"])

            self.assertIn(zip_code_search, zip_codes)

    def test_list_filter_by_address_zipcode_leading_zero(self):
        zip_code_search = "01234"
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url, {"address_postalcode": zip_code_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            zip_codes = []
            for location in location_entry["location"]:
                returned_location = self.client.get(location["reference"]).json()
                zip_codes.append(returned_location["address"]["postalCode"])

            self.assertIn(zip_code_search, zip_codes)

    def test_retrieve_non_existent_organization_affil(self):
        url = reverse(
            "fhir-organizationaffiliation-detail", args=["12300000-0000-0000-0000-000000000123"]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_non_valid_organization_affil(self):
        url = reverse("fhir-organizationaffiliation-detail", args=[self.org_with_no_affiliation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
