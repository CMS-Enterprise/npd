from contextlib import ExitStack
from unittest import TestCase
from unittest.mock import patch

from fastapi.testclient import TestClient

from fastapi_app.main import app
import fastapi_app.main as main_module


class NoDjangoBootstrapTestCase(TestCase):
    def setUp(self):
        self.client = TestClient(app)

    def test_active_resource_routes_are_bound_to_native_handlers(self):
        self.assertEqual(
            main_module.list_practitioner_resources.__module__,
            "fastapi_app.practitioner_native_service",
        )
        self.assertEqual(
            main_module.get_practitioner_resource.__module__,
            "fastapi_app.practitioner_native_service",
        )
        self.assertEqual(
            main_module.list_organization_resources.__module__,
            "fastapi_app.organization_native_service",
        )
        self.assertEqual(
            main_module.get_organization_resource.__module__,
            "fastapi_app.organization_native_service",
        )
        self.assertEqual(
            main_module.list_location_resources.__module__,
            "fastapi_app.location_native_service",
        )
        self.assertEqual(
            main_module.get_location_resource.__module__,
            "fastapi_app.location_native_service",
        )
        self.assertEqual(
            main_module.list_endpoint_resources.__module__,
            "fastapi_app.endpoint_native_service",
        )
        self.assertEqual(
            main_module.get_endpoint_resource.__module__,
            "fastapi_app.endpoint_native_service",
        )
        self.assertEqual(
            main_module.list_practitioner_role_resources.__module__,
            "fastapi_app.practitioner_role_native_service",
        )
        self.assertEqual(
            main_module.get_practitioner_role_resource.__module__,
            "fastapi_app.practitioner_role_native_service",
        )
        self.assertEqual(
            main_module.list_organization_affiliation_resources.__module__,
            "fastapi_app.organization_affiliation_native_service",
        )
        self.assertEqual(
            main_module.get_organization_affiliation_resource.__module__,
            "fastapi_app.organization_affiliation_native_service",
        )

    def test_active_routes_do_not_call_ensure_django(self):
        list_result = type("ListResult", (), {"resources": [], "total_count": 0})

        with ExitStack() as stack:
            stack.enter_context(
                patch(
                    "fastapi_app._django.ensure_django",
                    side_effect=AssertionError("FastAPI route unexpectedly bootstrapped Django"),
                )
            )
            stack.enter_context(
                patch("fastapi_app.main.list_practitioner_resources", return_value=list_result())
            )
            stack.enter_context(
                patch("fastapi_app.main.list_organization_resources", return_value=list_result())
            )
            stack.enter_context(
                patch("fastapi_app.main.list_location_resources", return_value=list_result())
            )
            stack.enter_context(
                patch("fastapi_app.main.list_endpoint_resources", return_value=list_result())
            )
            stack.enter_context(
                patch("fastapi_app.main.list_practitioner_role_resources", return_value=list_result())
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.list_organization_affiliation_resources",
                    return_value=list_result(),
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_practitioner_resource",
                    return_value={"resourceType": "Practitioner", "id": "x"},
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_organization_resource",
                    return_value={"resourceType": "Organization", "id": "x"},
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_location_resource",
                    return_value={"resourceType": "Location", "id": "x"},
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_endpoint_resource",
                    return_value={"resourceType": "Endpoint", "id": "x"},
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_practitioner_role_resource",
                    return_value={"resourceType": "PractitionerRole", "id": "x"},
                )
            )
            stack.enter_context(
                patch(
                    "fastapi_app.main.get_organization_affiliation_resource",
                    return_value={"resourceType": "OrganizationAffiliation", "id": "x"},
                )
            )

            routes = [
                "/fhir/Practitioner/?page_size=1",
                "/fhir/Organization/?page_size=1",
                "/fhir/Location/?page_size=1",
                "/fhir/Endpoint/?page_size=1",
                "/fhir/PractitionerRole/?page_size=1",
                "/fhir/OrganizationAffiliation/?page_size=1",
                "/fhir/Practitioner/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/Organization/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/Location/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/Endpoint/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/PractitionerRole/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/OrganizationAffiliation/aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa/",
                "/fhir/metadata/",
                "/fhir/docs/schema/",
                "/fhir/healthCheck/",
            ]

            for route in routes:
                response = self.client.get(route)
                self.assertLess(response.status_code, 500, route)
