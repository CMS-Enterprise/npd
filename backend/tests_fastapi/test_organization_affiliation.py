from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from fastapi_app.main import app
from fastapi_app.organization_affiliation_service import OrganizationAffiliationListResult


class OrganizationAffiliationEndpointTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("fastapi_app.main.list_organization_affiliation_resources")
    def test_list_wraps_results_in_expected_envelope(self, mock_list_resources):
        mock_list_resources.return_value = OrganizationAffiliationListResult(
            resources=[
                {
                    "resourceType": "OrganizationAffiliation",
                    "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
                }
            ],
            total_count=1,
        )

        response = self.client.get("/fhir/OrganizationAffiliation/?page_size=1")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/fhir+json")
        payload = response.json()
        self.assertEqual(payload["count"], 1)
        self.assertEqual(payload["results"]["resourceType"], "Bundle")
        self.assertEqual(payload["results"]["total"], 1)
        self.assertEqual(
            payload["results"]["entry"][0]["resource"]["id"],
            "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        )

    @patch("fastapi_app.main.get_organization_affiliation_resource")
    def test_retrieve_returns_fhir_json(self, mock_get_resource):
        mock_get_resource.return_value = {
            "resourceType": "OrganizationAffiliation",
            "id": "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa",
        }

        response = self.client.get(
            "/fhir/OrganizationAffiliation/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/fhir+json")
        self.assertEqual(response.json()["resourceType"], "OrganizationAffiliation")

    def test_malformed_id_returns_text_html_404(self):
        response = self.client.get("/fhir/OrganizationAffiliation/999999")

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
        self.assertEqual(response.text, "Organization 999999 not found")

    @patch("fastapi_app.main.get_organization_affiliation_resource")
    def test_missing_uuid_returns_fhir_json_404(self, mock_get_resource):
        mock_get_resource.return_value = None

        response = self.client.get(
            "/fhir/OrganizationAffiliation/12300000-0000-0000-0000-000000000123"
        )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.headers["content-type"], "application/fhir+json")
        self.assertEqual(
            response.json()["detail"],
            "No OrganizationAffiliationView matches the given query.",
        )
