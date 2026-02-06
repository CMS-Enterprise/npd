from django.test import TestCase
from django.urls import resolve, reverse


class ProviderDirectorySpaRouting(TestCase):
    """
    Ensure that provider_directory routing is agnostic to paths.
    """

    def test_homepage_url_resolves_to_correct_view(self):
        resolver = resolve("/")
        self.assertEqual(resolver.view_name, "provider_directory:index")
        self.assertEqual(resolver.func.__name__, "index")

    def test_detail_url_resolves_with_path(self):
        resolver = resolve("/search/123/")
        self.assertEqual(resolver.view_name, "provider_directory:index_with_path")
        self.assertEqual(resolver.kwargs["path"], "search/123/")

    def test_reverse_index_returns_path(self):
        path = reverse("provider_directory:index")
        self.assertEqual(path, "/")

    def test_reverse_index_with_path_returns_path(self):
        path = reverse("provider_directory:index_with_path", kwargs={"path": "search/123"})
        self.assertEqual(path, "/search/123")


class FhirApiRouting(TestCase):
    """
    Ensure we maintain a consistent routing configuration, with or without trailing slashes.
    """

    def assert_valid_routing(self, path_views):
        for path, expected_view_name in path_views:
            with self.subTest(f"route {path}"):
                resolver = resolve(path)
                self.assertEqual(resolver.view_name, expected_view_name)

    def test_fhir_accepts_optional_trailing_slash(self):
        path_views = [
            ("/fhir", "api-root"),
            ("/fhir/", "api-root"),
        ]
        self.assert_valid_routing(path_views)

    def test_fhir_docs_accepts_optional_trailing_slash(self):
        path_views = [
            ("/fhir/docs", "schema-swagger-ui"),
            ("/fhir/docs/", "schema-swagger-ui"),
            # fallthrough
            ("/fhirdocs", "provider_directory:index_with_path"),
            ("/fhirdocs/", "provider_directory:index_with_path"),
        ]
        self.assert_valid_routing(path_views)

    def test_fhir_rest_routes_accept_optional_trailing_slash(self):
        path_views = [
            # valid paths
            ("/fhir/Endpoint", "fhir-endpoint-list"),
            ("/fhir/Endpoint/", "fhir-endpoint-list"),
            ("/fhir/Endpoint/12345", "fhir-endpoint-detail"),
            ("/fhir/Endpoint/12345/", "fhir-endpoint-detail"),
            # fallthrough
            ("/fhirEndpoint", "provider_directory:index_with_path"),
            ("/fhirEndpoint/", "provider_directory:index_with_path"),
            ("/fhirEndpoint/12345", "provider_directory:index_with_path"),
            ("/fhirEndpoint/12345/", "provider_directory:index_with_path"),
            ("/fhir/Endpoint12345", "provider_directory:index_with_path"),
            ("/fhir/Endpoint12345/", "provider_directory:index_with_path"),
            ("/fhirEndpoint12345", "provider_directory:index_with_path"),
            ("/fhirEndpoint12345/", "provider_directory:index_with_path"),
        ]
        self.assert_valid_routing(path_views)

    def test_fhir_rest_routes_reverse_without_slash(self):
        endpoint_list_path = reverse("fhir-endpoint-list")
        self.assertEqual(endpoint_list_path, "/fhir/Endpoint")

        endpoint_detail_path = reverse("fhir-endpoint-detail", kwargs={"id": 12345})
        self.assertEqual(endpoint_detail_path, "/fhir/Endpoint/12345")
