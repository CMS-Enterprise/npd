import uuid

from django.urls import reverse
from rest_framework import status

from ..models import (
    EhrVendor,
    LocationToEndpointInstance,
    Nucc,
    Organization,
    OtherIdType,
)
from .api_test_case import APITestCase
from .fixtures.endpoint import create_endpoint_instance
from .fixtures.location import create_location
from .fixtures.organization import create_organization, create_legal_entity
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

        # -----------------------------
        # Reference data
        # -----------------------------
        legal_entity = create_legal_entity("Good Health EIN")
        other_id_type = OtherIdType.objects.get(value="MEDICAID")

        nucc = Nucc.objects.get(code="261Q00000X")

        ehr_vendor = EhrVendor.objects.create(
            id=uuid.uuid4(),
            name="Epic",
            is_cms_aligned_network=True,
        )

        ehr_vendor2 = EhrVendor.objects.create(
            id=uuid.uuid4(),
            name="Legendary",
            is_cms_aligned_network=True,
        )

        ehr_vendor3 = EhrVendor.objects.create(
            id=uuid.uuid4(),
            name="Zod",
            is_cms_aligned_network=True,
        )

        # =========================================================
        # ✅ MATCHING ORGANIZATION #1 (FULLY QUALIFIED)
        # =========================================================
        cls.org_good_1 = create_organization(
            name="A Good Clinical Org",
            legal_entity=legal_entity,
            other_id_type=other_id_type,
            organization_type=nucc.code,
        )

        cls.orgs.append(cls.org_good_1)

        loc_good_1 = create_location(
            organization=cls.org_good_1,
            name="Good Location 1",
        )

        endpoint_instance = create_endpoint_instance(
            organization=cls.org_good_1,
            name="Good Endpoint 1",
            ehr=ehr_vendor3,
        )

        LocationToEndpointInstance.objects.create(
            location=loc_good_1,
            endpoint_instance=endpoint_instance,
        )

        # =========================================================
        # ✅ MATCHING ORGANIZATION #2 (MULTIPLE LOCATIONS / ENDPOINTS)
        # =========================================================
        cls.org_good_2 = create_organization(
            name="B Good Clinical Org",
            legal_entity=legal_entity,
        )

        cls.orgs.append(cls.org_good_2)

        loc_good_2a = create_location(organization=cls.org_good_2, name="Location A")
        loc_good_2b = create_location(organization=cls.org_good_2, name="Location B")

        endpoint_good_2a = create_endpoint_instance(
            organization=cls.org_good_2,
            name="Endpoint A",
            ehr=ehr_vendor,
        )

        endpoint_good_2b = create_endpoint_instance(
            organization=cls.org_good_2,
            name="Endpoint B",
            ehr=ehr_vendor,
        )

        LocationToEndpointInstance.objects.create(
            location=loc_good_2a,
            endpoint_instance=endpoint_good_2a,
        )
        LocationToEndpointInstance.objects.create(
            location=loc_good_2b,
            endpoint_instance=endpoint_good_2b,
        )

        # =========================================================
        # ✅ MATCHING ORGANIZATION #3 (MULTIPLE LOCATIONS / ENDPOINTS)
        # =========================================================
        cls.org_good_3 = create_organization(
            name="C Good Clinical Org",
            legal_entity=legal_entity,
        )

        cls.orgs.append(cls.org_good_3)

        loc_good_3a = create_location(organization=cls.org_good_3, name="Location C")
        loc_good_3b = create_location(organization=cls.org_good_3, name="Location D")

        endpoint_good_3a = create_endpoint_instance(
            organization=cls.org_good_3,
            name="Endpoint A",
            ehr=ehr_vendor2,
        )

        endpoint_good_3b = create_endpoint_instance(
            organization=cls.org_good_3,
            name="Endpoint B",
            ehr=ehr_vendor2,
        )

        LocationToEndpointInstance.objects.create(
            location=loc_good_3a,
            endpoint_instance=endpoint_good_3a,
        )
        LocationToEndpointInstance.objects.create(
            location=loc_good_3b,
            endpoint_instance=endpoint_good_3b,
        )

        # =========================================================
        # ❌ NON-MATCHING #1 — NO LOCATION
        # =========================================================
        cls.invalid_1 = create_organization(
            name="No Location Org",
            legal_entity=legal_entity,
        )

        # =========================================================
        # ❌ NON-MATCHING #2 — LOCATION BUT NO ENDPOINT
        # =========================================================
        cls.org_no_endpoint = create_organization(name="No Endpoint Org")
        create_location(organization=cls.org_no_endpoint)

        # =========================================================
        # ❌ NON-MATCHING #4 — ENDPOINT NOT LINKED TO LOCATION
        # =========================================================
        cls.org_unlinked = create_organization(name="Unlinked Endpoint Org")
        create_location(organization=cls.org_unlinked)

        create_endpoint_instance(
            organization=cls.org_unlinked,
            name="Dangling Endpoint",
            ehr=ehr_vendor,
        )

        return super().setUpTestData()

    def setUp(self):
        super().setUp()
        self.org_without_authorized_official = Organization.objects.create(
            id="26708690-19d6-499e-b481-cebe05b98f08", authorized_official_id=None
        )

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

        valid_ids = [str(org.id) for org in self.orgs]

        self.assertEqual(ids, valid_ids)

    def test_list_does_not_have_incorrect_orgs(self):
        url = reverse("fhir-organizationaffiliation-list")
        response = self.client.get(url)

        ids = extract_resource_ids(response)

        self.assertNotIn(str(self.invalid_1.id), ids)
        self.assertNotIn(str(self.org_no_endpoint.id), ids)
        self.assertNotIn(str(self.org_unlinked.id), ids)

    def test_retrieve_single_organization_affil(self):
        url = reverse("fhir-organizationaffiliation-detail", args=[self.orgs[0].id])
        response = self.client.get(url)

        self.assertEqual(str(self.orgs[0].id), response.data["id"])

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
        url = reverse("fhir-organizationaffiliation-detail", args=[self.invalid_1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
