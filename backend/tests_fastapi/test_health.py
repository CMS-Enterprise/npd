from unittest import TestCase

from fastapi.testclient import TestClient

from fastapi_app.main import app


class HealthEndpointTestCase(TestCase):
    def test_healthcheck_returns_plain_text(self):
        client = TestClient(app)
        response = client.get("/fhir/healthCheck")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.text, "healthy")

