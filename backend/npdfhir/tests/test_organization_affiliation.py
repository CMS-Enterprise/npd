from django.urls import reverse
from rest_framework import status
from .api_test_case import APITestCase
from .fixtures.endpoint import DefaultEhrVendor, DefaultEndpointInstance
from .fixtures.organization import DefaultOrganization, DefaultLocation
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    extract_resource_ids,
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
            id="a9cd57b1-9e8c-4b75-86da-653acfc3ade6",
            locations=[
                DefaultLocation(
                    name="Good Location 1",
                    endpoint_instance=DefaultEndpointInstance(name="Good Endpoint 1"),
                )
            ],
        )
        cls.orgs.append(org)

        # Generate test data for an organization with multiple endpoints, same EHR vendor
        org = DefaultOrganization(
            locations=[
                DefaultLocation(
                    name="Location A",
                    endpoint_instance=DefaultEndpointInstance(name="Endpoint A"),
                ),
                DefaultLocation(
                    name="Location B",
                    endpoint_instance=DefaultEndpointInstance(name="Endpoint B"),
                ),
            ]
        )
        cls.orgs.append(org)

        # Generate test data for an organization with multiple endpoints, different EHR vendors
        org = DefaultOrganization(
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
            ]
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

    #    def test_list_in_default_order(self):
    #        url = reverse("fhir-organizationaffiliation-list")
    #        response = self.client.get(url)
    #        assert_fhir_response(self, response)
    #
    #        particpiationg_orgs = extract_resource_fields(response, "participatingOrganization")
    #        participating_org_names = [org["display"] for org in particpiationg_orgs]
    #
    #        sorted = ["A Good Clinical Org", "B Good Clinical Org", "C Good Clinical Org"]
    #
    #        self.assertEqual(
    #            participating_org_names,
    #            sorted,
    #            f"Expected fhir org affilations sorted by participating org name but got {participating_org_names}\n Sorted: {sorted}",
    #        )
    #
    #    def test_list_in_descending_order(self):
    #        url = reverse("fhir-organizationaffiliation-list")
    #        response = self.client.get(url, {"_sort": "-organization_name"})
    #        assert_fhir_response(self, response)
    #
    #        particpiationg_orgs = extract_resource_fields(response, "participatingOrganization")
    #        participating_org_names = [org["display"] for org in particpiationg_orgs]
    #
    #        sorted = ["C Good Clinical Org", "B Good Clinical Org", "A Good Clinical Org"]
    #
    #        self.assertEqual(
    #            participating_org_names,
    #            sorted,
    #            f"Expected fhir org affilations sorted in descending order by participating org name but got {participating_org_names}\n Sorted: {sorted}",
    #        )
    #
    #    def test_list_in_ehr_vendor_order(self):
    #        url = reverse("fhir-organizationaffiliation-list")
    #        response = self.client.get(url, {"_sort": "ehr_vendor_name"})
    #        assert_fhir_response(self, response)
    #
    #        ehr_orgs = extract_resource_fields(response, "organization")
    #        ehr_org_names = [org["display"] for org in ehr_orgs]
    #
    #        sorted = ["Epic", "Legendary", "Zod"]
    #
    #        self.assertEqual(
    #            ehr_org_names,
    #            sorted,
    #            f"Expected fhir org affilations sorted in descending order by ehr org name but got {ehr_org_names}\n Sorted: {sorted}",
    #        )

    def test_list_has_correct_orgs(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)

        ids = extract_resource_ids(response)
        ids.sort()

        valid_ids = [str(org.id) for org in self.orgs]
        valid_ids.sort()

        self.assertEqual(ids, valid_ids)

    def test_list_does_not_have_incorrect_orgs(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)

        ids = extract_resource_ids(response)

        self.assertNotIn(str(self.org_with_no_affiliation.id), ids)
        self.assertNotIn(str(self.org_with_no_location.id), ids)

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

    def test_retrieve_non_existant_organization_affil(self):
        url = reverse(
            "fhir-organizationaffiliation-detail", args=["12300000-0000-0000-0000-000000000123"]
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_non_valid_organization_affil(self):
        url = reverse("fhir-organizationaffiliation-detail", args=[self.org_with_no_affiliation.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
