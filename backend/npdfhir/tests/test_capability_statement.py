from django.urls import reverse
from fhir.resources.R4B.capabilitystatement import CapabilityStatement
from rest_framework import status

from .api_test_case import APITestCase


class CapabilityStatementViewSetTestCase(APITestCase):
    def setUp(self):
        super().setUp()
        self.url = reverse("fhir-metadata")

    # Response tests
    def test_capability_statement_returns_200(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_capability_statement_returns_correct_content_type(self):
        response = self.client.get(self.url)
        self.assertEqual(response["Content-Type"], "application/fhir+json")

    # Content tests
    def test_capability_statement_has_resource_type(self):
        response = self.client.get(self.url)
        self.assertEqual(response.data["resourceType"], "CapabilityStatement")

    def test_capability_statement_has_required_fields(self):
        response = self.client.get(self.url)
        data = response.data

        self.assertIn("status", data)
        self.assertIn("fhirVersion", data)
        self.assertIn("format", data)
        self.assertIn("rest", data)

    # Validation tests
    def test_capability_statement_is_valid_fhir(self):
        response = self.client.get(self.url)

        capability_statement = CapabilityStatement.model_validate(response.data)
        self.assertEqual(capability_statement.__resource_type__, "CapabilityStatement")
