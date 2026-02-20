from django.urls import reverse
from rest_framework import status

from .api_test_case import APITestCase
from ..documentation_content import docs


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


class DocumentationContentFilterTestCase(APITestCase):
    # Verify each endpoints filters has correct content
    def setUp(self):
        super().setUp()
        schema_url = reverse("schema")
        response = self.client.get(schema_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.schema = response.data
        self.paths = self.schema.get("paths", {})

    def get_parameter_description(self, path, param_name):
        # Helper to extract a parameter's description from the schema
        operation = self.paths.get(path, {}).get("get", {})
        parameters = operation.get("parameters", [])
        for param in parameters:
            if param.get("name") == param_name:
                return param.get("description", "")
        return None

    # Practitioner Filter Tests
    def test_practitioner_name_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "name")
        self.assertIsNotNone(description, "name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.name))

    def test_practitioner_gender_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "gender")
        self.assertIsNotNone(description, "gender parameter not found in schema")
        self.assertIn(str(docs.filters.practitioner.gender), description)

    def test_practitioner_identifier_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "identifier")
        self.assertIsNotNone(description, "identifier parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.identifier))

    def test_practitioner_type_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "practitioner_type")
        self.assertIsNotNone(description, "practitioner_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.type))

    def test_practitioner_address_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "address")
        self.assertIsNotNone(description, "address parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.full))

    def test_practitioner_address_city_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "address_city")
        self.assertIsNotNone(description, "address_city parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.city))

    def test_practitioner_address_state_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "address_state")
        self.assertIsNotNone(description, "address_state parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.state))

    def test_practitioner_address_postalcode_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "address_postalcode")
        self.assertIsNotNone(description, "address_postalcode parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.postalcode))

    def test_practitioner_address_use_filter_description(self):
        description = self.get_parameter_description("/fhir/Practitioner/", "address_use")
        self.assertIsNotNone(description, "address_use parameter not found in schema")
        self.assertIn(str(docs.filters.address.use), description)

    # Organization Filter Tests
    def test_organization_name_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "name")
        self.assertIsNotNone(description, "name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.name))

    def test_organization_identifier_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "identifier")
        self.assertIsNotNone(description, "identifier parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.identifier))

    def test_organization_type_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "organization_type")
        self.assertIsNotNone(description, "organization_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.type))

    def test_organization_address_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "address")
        self.assertIsNotNone(description, "address parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.full))

    def test_organization_address_city_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "address_city")
        self.assertIsNotNone(description, "address_city parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.city))

    def test_organization_address_state_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "address_state")
        self.assertIsNotNone(description, "address_state parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.state))

    def test_organization_address_postalcode_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "address_postalcode")
        self.assertIsNotNone(description, "address_postalcode parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.postalcode))

    def test_organization_address_use_filter_description(self):
        description = self.get_parameter_description("/fhir/Organization/", "address_use")
        self.assertIsNotNone(description, "address_use parameter not found in schema")
        self.assertIn(str(docs.filters.address.use), description)

    # Location Filter Tests
    def test_location_name_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "name")
        self.assertIsNotNone(description, "name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.location.name))

    def test_location_organization_type_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "organization_type")
        self.assertIsNotNone(description, "organization_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.type))

    def test_location_address_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "address")
        self.assertIsNotNone(description, "address parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.full))

    def test_location_address_city_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "address_city")
        self.assertIsNotNone(description, "address_city parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.city))

    def test_location_address_state_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "address_state")
        self.assertIsNotNone(description, "address_state parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.state))

    def test_location_address_postalcode_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "address_postalcode")
        self.assertIsNotNone(description, "address_postalcode parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.postalcode))

    def test_location_address_use_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "address_use")
        self.assertIsNotNone(description, "address_use parameter not found in schema")
        self.assertIn(str(docs.filters.address.use), description)

    def test_location_near_filter_description(self):
        description = self.get_parameter_description("/fhir/Location/", "near")
        self.assertIsNotNone(description, "near parameter not found in schema")
        self.assertEqual(description, str(docs.filters.location.near))

    # Endpoint Filter Tests
    def test_endpoint_name_filter_description(self):
        description = self.get_parameter_description("/fhir/Endpoint/", "name")
        self.assertIsNotNone(description, "name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.name))

    def test_endpoint_connection_type_filter_description(self):
        description = self.get_parameter_description("/fhir/Endpoint/", "connection_type")
        self.assertIsNotNone(description, "connection_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.connection_type))

    def test_endpoint_payload_type_filter_description(self):
        description = self.get_parameter_description("/fhir/Endpoint/", "payload_type")
        self.assertIsNotNone(description, "payload_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.payload_type))

    def test_endpoint_status_filter_description(self):
        description = self.get_parameter_description("/fhir/Endpoint/", "status")
        self.assertIsNotNone(description, "status parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.status))

    # PractitionerRole Filter Tests
    def test_practitioner_role_practitioner_name_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "practitioner_name")
        self.assertIsNotNone(description, "practitioner_name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.name))

    def test_practitioner_role_practitioner_gender_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "practitioner_gender"
        )
        self.assertIsNotNone(description, "practitioner_gender parameter not found in schema")
        self.assertIn(str(docs.filters.practitioner.gender), description)

    def test_practitioner_role_practitioner_type_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "practitioner_type")
        self.assertIsNotNone(description, "practitioner_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.type))

    def test_practitioner_role_practitioner_identifier_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "practitioner_identifier"
        )
        self.assertIsNotNone(description, "practitioner_identifier parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner.identifier))

    def test_practitioner_role_organization_name_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "organization_name")
        self.assertIsNotNone(description, "organization_name parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.name))

    def test_practitioner_role_organization_type_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "organization_type")
        self.assertIsNotNone(description, "organization_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.organization.type))

    def test_practitioner_role_location_near_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "location_near")
        self.assertIsNotNone(description, "location_near parameter not found in schema")
        self.assertEqual(description, str(docs.filters.location.near))

    def test_practitioner_role_location_address_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "location_address")
        self.assertIsNotNone(description, "location_address parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.full))

    def test_practitioner_role_location_address_city_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "location_address_city"
        )
        self.assertIsNotNone(description, "location_address_city parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.city))

    def test_practitioner_role_location_address_state_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "location_address_state"
        )
        self.assertIsNotNone(description, "location_address_state parameter not found in schema")
        self.assertEqual(description, str(docs.filters.address.state))

    def test_practitioner_role_location_address_postalcode_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "location_address_postalcode"
        )
        self.assertIsNotNone(
            description, "location_address_postalcode parameter not found in schema"
        )
        self.assertEqual(description, str(docs.filters.address.postalcode))

    def test_practitioner_role_active_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "active")
        self.assertIsNotNone(description, "active parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner_role.active))

    def test_practitioner_role_role_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "role")
        self.assertIsNotNone(description, "role parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner_role.role))

    def test_practitioner_role_specialty_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "specialty")
        self.assertIsNotNone(description, "specialty parameter not found in schema")
        self.assertEqual(description, str(docs.filters.practitioner_role.specialty))

    def test_practitioner_role_endpoint_connection_type_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "endpoint_connection_type"
        )
        self.assertIsNotNone(description, "endpoint_connection_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.connection_type))

    def test_practitioner_role_endpoint_payload_type_filter_description(self):
        description = self.get_parameter_description(
            "/fhir/PractitionerRole/", "endpoint_payload_type"
        )
        self.assertIsNotNone(description, "endpoint_payload_type parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.payload_type))

    def test_practitioner_role_endpoint_status_filter_description(self):
        description = self.get_parameter_description("/fhir/PractitionerRole/", "endpoint_status")
        self.assertIsNotNone(description, "endpoint_status parameter not found in schema")
        self.assertEqual(description, str(docs.filters.endpoint.status))


class DocumentationContentEndpointDescriptionTestCase(APITestCase):
    # Verify endpoints operations (list/retrieve/get) have correct descriptions
    def setUp(self):
        super().setUp()
        schema_url = reverse("schema")
        response = self.client.get(schema_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.schema = response.data
        self.paths = self.schema.get("paths", {})

    def get_operation_description(self, path, method="get"):
        """Helper to extract an operation's description from the schema"""
        return self.paths.get(path, {}).get(method, {}).get("description", "")

    # Practitioner Endpoint
    def test_practitioner_list_description(self):
        description = self.get_operation_description("/fhir/Practitioner/")
        self.assertIn(str(docs.endpoints.practitioner.list_description), description)

    def test_practitioner_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/Practitioner/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.practitioner.default_sort), description)

    def test_practitioner_retrieve_description(self):
        description = self.get_operation_description("/fhir/Practitioner/{id}/")
        self.assertIn(str(docs.endpoints.practitioner.retrieve_description), description)

    # PractitionerRole Endpoint
    def test_practitioner_role_list_description(self):
        description = self.get_operation_description("/fhir/PractitionerRole/")
        self.assertIn(str(docs.endpoints.practitioner_role.list_description), description)

    def test_practitioner_role_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/PractitionerRole/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.practitioner_role.default_sort), description)

    def test_practitioner_role_retrieve_description(self):
        description = self.get_operation_description("/fhir/PractitionerRole/{id}/")
        self.assertIn(str(docs.endpoints.practitioner_role.retrieve_description), description)

    # Organization Endpoint
    def test_organization_list_description(self):
        description = self.get_operation_description("/fhir/Organization/")
        self.assertIn(str(docs.endpoints.organization.list_description), description)

    def test_organization_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/Organization/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.organization.default_sort), description)

    def test_organization_retrieve_description(self):
        description = self.get_operation_description("/fhir/Organization/{id}/")
        self.assertIn(str(docs.endpoints.organization.retrieve_description), description)

    # Location Endpoint
    def test_location_list_description(self):
        description = self.get_operation_description("/fhir/Location/")
        self.assertIn(str(docs.endpoints.location.list_description), description)

    def test_location_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/Location/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.location.default_sort), description)

    def test_location_retrieve_description(self):
        description = self.get_operation_description("/fhir/Location/{id}/")
        self.assertIn(str(docs.endpoints.location.retrieve_description), description)

    # Endpoint Endpoint
    def test_endpoint_list_description(self):
        description = self.get_operation_description("/fhir/Endpoint/")
        self.assertIn(str(docs.endpoints.endpoint.list_description), description)

    def test_endpoint_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/Endpoint/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.endpoint.default_sort), description)

    def test_endpoint_retrieve_description(self):
        description = self.get_operation_description("/fhir/Endpoint/{id}/")
        self.assertIn(str(docs.endpoints.endpoint.retrieve_description), description)

    # OrganizationAffiliation Endpoint
    def test_organization_affiliation_list_description(self):
        description = self.get_operation_description("/fhir/OrganizationAffiliation/")
        self.assertIn(str(docs.endpoints.organization_affiliation.list_description), description)

    def test_organization_affiliation_list_includes_default_sort(self):
        description = self.get_operation_description("/fhir/OrganizationAffiliation/")
        self.assertIn(str(docs.constants.sort_order_text), description)
        self.assertIn(str(docs.endpoints.organization_affiliation.default_sort), description)

    def test_organization_affiliation_retrieve_description(self):
        description = self.get_operation_description("/fhir/OrganizationAffiliation/{id}/")
        self.assertIn(
            str(docs.endpoints.organization_affiliation.retrieve_description), description
        )

    # CapabilityStatement Endpoint
    def test_capability_statement_description(self):
        description = self.get_operation_description("/fhir/metadata/")
        self.assertIn(str(docs.endpoints.capability_statement.get_description), description)


class DocumentationContentResponseTestCase(APITestCase):
    # Verify endpoint responses has correct response descriptions
    def setUp(self):
        super().setUp()
        schema_url = reverse("schema")
        response = self.client.get(schema_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.schema = response.data
        self.paths = self.schema.get("paths", {})

    def get_response_description(self, path, method="get", status_code="200"):
        # Helper to extract a response description from the schema
        return (
            self.paths.get(path, {})
            .get(method, {})
            .get("responses", {})
            .get(status_code, {})
            .get("description", "")
        )

    # Practitioner Response
    def test_practitioner_list_response_description(self):
        description = self.get_response_description("/fhir/Practitioner/")
        self.assertEqual(description, str(docs.endpoints.practitioner.list_response))

    def test_practitioner_retrieve_response_description(self):
        description = self.get_response_description("/fhir/Practitioner/{id}/")
        self.assertEqual(description, str(docs.endpoints.practitioner.retrieve_response))

    # PractitionerRole Response
    def test_practitioner_role_list_response_description(self):
        description = self.get_response_description("/fhir/PractitionerRole/")
        self.assertEqual(description, str(docs.endpoints.practitioner_role.list_response))

    def test_practitioner_role_retrieve_response_description(self):
        description = self.get_response_description("/fhir/PractitionerRole/{id}/")
        self.assertEqual(description, str(docs.endpoints.practitioner_role.retrieve_response))

    # Organization Response
    def test_organization_list_response_description(self):
        description = self.get_response_description("/fhir/Organization/")
        self.assertEqual(description, str(docs.endpoints.organization.list_response))

    def test_organization_retrieve_response_description(self):
        description = self.get_response_description("/fhir/Organization/{id}/")
        self.assertEqual(description, str(docs.endpoints.organization.retrieve_response))

    # Location Response
    def test_location_list_response_description(self):
        description = self.get_response_description("/fhir/Location/")
        self.assertEqual(description, str(docs.endpoints.location.list_response))

    def test_location_retrieve_response_description(self):
        description = self.get_response_description("/fhir/Location/{id}/")
        self.assertEqual(description, str(docs.endpoints.location.retrieve_response))

    # Endpoint Response
    def test_endpoint_list_response_description(self):
        description = self.get_response_description("/fhir/Endpoint/")
        self.assertEqual(description, str(docs.endpoints.endpoint.list_response))

    def test_endpoint_retrieve_response_description(self):
        description = self.get_response_description("/fhir/Endpoint/{id}/")
        self.assertEqual(description, str(docs.endpoints.endpoint.retrieve_response))

    # OrganizationAffiliation Response
    def test_organization_affiliation_list_response_description(self):
        description = self.get_response_description("/fhir/OrganizationAffiliation/")
        self.assertEqual(description, str(docs.endpoints.organization_affiliation.list_response))

    def test_organization_affiliation_retrieve_response_description(self):
        description = self.get_response_description("/fhir/OrganizationAffiliation/{id}/")
        self.assertEqual(
            description, str(docs.endpoints.organization_affiliation.retrieve_response)
        )

    # CapabilityStatement Response
    def test_capability_statement_response_description(self):
        description = self.get_response_description("/fhir/metadata/")
        self.assertEqual(description, str(docs.endpoints.capability_statement.get_response))
