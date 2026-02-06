from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase


class DocumentationViewSetTestCase(APITestCase):
    def test_get_swagger_docs(self):
        swagger_url = reverse("schema-swagger-ui")
        response = self.client.get(swagger_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('id="swagger-ui"', response.text)

    def test_get_redoc_docs(self):
        redoc_url = reverse("schema-redoc")
        response = self.client.get(redoc_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("redoc spec-url", response.text)

    def test_get_json_docs(self):
        json_docs_url = reverse("schema")
        response = self.client.get(json_docs_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("application/vnd.oai.openapi+json", response["Content-Type"])
        self.assertIn("openapi", response.data.keys())
