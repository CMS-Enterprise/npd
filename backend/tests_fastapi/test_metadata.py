from unittest import TestCase

from fastapi.testclient import TestClient

from fastapi_app.main import app


class MetadataEndpointTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_metadata_matches_expected_contract_shape(self):
        response = self.client.get("/fhir/metadata/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/fhir+json")

        payload = response.json()
        self.assertEqual(payload["resourceType"], "CapabilityStatement")
        self.assertEqual(payload["version"], "beta")
        self.assertEqual(payload["name"], "FHIRCapablityStatement")
        self.assertEqual(payload["title"], "NPD FHIR API -  FHIR Capablity Statement")
        self.assertEqual(payload["status"], "active")
        self.assertEqual(payload["publisher"], "CMS")
        self.assertEqual(payload["kind"], "instance")
        self.assertEqual(payload["fhirVersion"], "4.0.1")
        self.assertEqual(payload["format"], ["fhir+json"])
        self.assertEqual(payload["contact"][0]["telecom"][0]["value"], "npd@cms.hhs.gov")
        self.assertEqual(payload["implementation"]["url"], "http://testserver/fhir")
        self.assertEqual(payload["rest"][0]["documentation"], "All FHIR endpoints for the National Provider Directory")
        self.assertEqual(
            [resource["type"] for resource in payload["rest"][0]["resource"]],
            ["Practitioner", "Organization", "Endpoint", "Location", "PractitionerRole"],
        )

    def test_metadata_honors_fhir_json_accept_header(self):
        response = self.client.get(
            "/fhir/metadata/",
            headers={"Accept": "application/fhir+json"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/fhir+json")
        self.assertEqual(response.json()["resourceType"], "CapabilityStatement")

    def test_schema_endpoint_returns_openapi_json(self):
        response = self.client.get("/fhir/docs/schema/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "application/vnd.oai.openapi+json")
        payload = response.json()
        self.assertEqual(payload["info"]["title"], "National Provider Directory API")
        self.assertIn("/fhir/Practitioner/", payload["paths"])

    def test_swagger_ui_endpoint_returns_html(self):
        response = self.client.get("/fhir/docs/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
        self.assertIn("Swagger UI", response.text)
        self.assertIn("/fhir/docs/schema/", response.text)

    def test_redoc_endpoint_returns_html(self):
        response = self.client.get("/fhir/docs/redoc/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.headers["content-type"], "text/html; charset=utf-8")
        self.assertIn("ReDoc", response.text)
        self.assertIn("/fhir/docs/schema/", response.text)
