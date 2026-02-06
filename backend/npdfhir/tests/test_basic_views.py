from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase


class BasicViewsTestCase(APITestCase):
    def test_health_view(self):
        url = reverse("healthCheck")  # maps to "/healthCheck"
        response = self.client.get(url)
        res_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(res_obj["status"], "healthy")

    def test_fhir_endpoint_list_without_slash(self):
        response = self.client.get("/fhir")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_fhir_endpoint_list_with_slash(self):
        response = self.client.get("/fhir/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
