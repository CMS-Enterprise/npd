from django.urls import reverse
from rest_framework import status

from geopy.distance import geodesic

from .api_test_case import APITestCase
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    # extract_resource_ids,
)

from ..models import (
    OrganizationToName,
    Provider,
    IndividualToName,
    ProviderView,
    ProviderToLocationView,
    Organization,
    OrganizationView,
)

from .fixtures.address import DefaultAddress
from .fixtures.organization import DefaultLocation, DefaultOrganization
from .fixtures.practitioner_role import DefaultPractitionerRole
from .fixtures.practitioner import DefaultPractitioner, DefaultIndividual, DefaultName, DefaultNPI
from .fixtures.endpoint import DefaultEndpointInstance


class PractitionerRoleViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Generate test data for various locations
        locations = [
            {
                "id": "3719c831-a4b7-4a7f-bb47-465a024384fc",
                "name": "ABACUS BUSINESS CORPORATION GROUP INC.",
                "address": {
                    "city": "San Diego",
                    "state": "CA",
                    "zip_code": "05555",
                    "line_1": "404 Great Amazing Avenue",
                    "x": 32.824056,
                    "y": -117.437397,
                },
            },
            {
                "id": "7c7a433b-fca7-4fb2-9283-dc764fb0ed5c",
                "name": "ABBY D CENTER, INC.",
                "address": {
                    "city": "Seattle",
                    "state": "WA",
                    "zip_code": "77777",
                    "line_1": "333 Grunge Blvd.",
                    "x": 47.608597,
                    "y": -122.5046021,
                },
            },
            {
                "id": "6df24407-ebe0-4f0b-9a75-bdfee486f0df",
                "name": "ABC DURABLE MEDICAL EQUIPMENT INC",
                "address": {
                    "city": "St. Louis",
                    "state": "MO",
                    "zip_code": "89898",
                    "line_1": "66 Arch Lane",
                    "x": 38.6219297,
                    "y": -90.182935,
                },
            },
            {
                "id": "c1fc1ada-841a-4b92-9e8e-37f4d17b65d4",
                "name": "ABC HOME MEDICAL SUPPLY, INC.",
                "address": {
                    "city": "St. Louis",
                    "state": "MO",
                    "zip_code": "65313",
                    "line_1": "City Museum Rd.",
                    "x": 38.6336745,
                    "y": -90.2032725,
                },
            },
            {
                "id": "b7517cc7-b406-4932-9856-6983ac4ec308",
                "name": "A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
                "address": {
                    "city": "Ft. Lauderdale",
                    "state": "FL",
                    "zip_code": "43433",
                    "line_1": "789 Palmetto Road",
                    "x": 26.1412097,
                    "y": -80.1910040,
                },
            },
        ]

        for location in locations:
            DefaultPractitionerRole(
                location=DefaultLocation(
                    id=location["id"],
                    name=location["name"],
                    address=DefaultAddress(**location["address"]),
                )
            )

        # Generate test data for a practitioner role with specific details

        # Optimetrist practitioner
        pr = DefaultPractitionerRole(
            practitioner=DefaultPractitioner(
                individual=DefaultIndividual(
                    names=[DefaultName({"first_name": "Charlie", "last_name": "Brown"})], gender="M"
                ),
                npi=DefaultNPI(npi=3000000001),
                taxonomies=["152W00000X"],
            ),
            organization=DefaultOrganization(
                names=["Charlie Brown M.D."], taxonomies=["261Q00000X"]
            ),
            location=DefaultLocation(
                address=DefaultAddress(city="Sunnyville", state="CA", zip_code="90001"),
                endpoint_instance=DefaultEndpointInstance(
                    payload_type="urn:ihe:pcc:xphr:2007", connection_type="secure-email"
                ),
            ),
            specialty=777,
        )
        cls.organization_id = pr.organization.id

        # Generate test data to retrieve specific practitioner role
        DefaultPractitionerRole(id="cad156c0-87fb-489b-bf5e-f15c95ee771e")

        OrganizationView.refresh_materialized_view()
        ProviderView.refresh_materialized_view()
        ProviderToLocationView.refresh_materialized_view()

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    """def test_list_in_proper_order(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # Extract ids
        ids = extract_resource_ids(response)

        sorted_ids = [str(role.id) for role in self.roles]

        self.assertEqual(
            ids,
            sorted_ids,
            f"Expected Practitioner roles sorted by order of location name but got {ids}\n Sorted: {sorted_ids}",
        )"""

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Filter tests.
    def test_list_filter_by_y_name(self):
        sample_name = "Charly"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_name": sample_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            # Query the practitioner names based on the returned id
            practitioner_id = entry["resource"]["practitioner"]["reference"].split("/")[-1]
            provider = Provider.objects.select_related("individual").get(
                individual_id=practitioner_id
            )

            name_objects = IndividualToName.objects.filter(individual=provider.individual).all()

            # Save if the search matches an individual name associated with a provider
            match_conditions = []

            for name in name_objects:
                name_string = ""
                name_string += f"{name.prefix or ''}"
                name_string += f"{name.first_name or ''} {name.middle_name or ''}"
                name_string += f"{name.last_name or ''} {name.suffix or ''}"

                match_conditions.append(sample_name in name_string)

            # Make sure that the provider has any individual name that matches
            self.assertTrue(any(match_conditions))

    def test_list_filter_by_practitioner_gender(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_gender": "Female"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            # Query the practitioner individual based on the returned id
            practitioner_id = entry["resource"]["practitioner"]["reference"].split("/")[-1]
            provider = Provider.objects.select_related("individual").get(
                individual_id=practitioner_id
            )

            self.assertEqual("F", provider.individual.gender)

    def test_list_filter_by_organization_name(self):
        name_search = "Charly Brown M.D."
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_name": name_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            # Query the practitioner names based on the returned id
            org_id = entry["resource"]["organization"]["reference"].split("/")[-1]
            org_name = (
                OrganizationToName.objects.filter(organization_id=org_id)
                .values_list("name", flat=True)
                .first()
            )

            self.assertIn(name_search, org_name)

    def test_list_filter_by_organization_y_name(self):
        name_search = "Charly"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_name": name_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            # Query the practitioner names based on the returned id
            org_id = entry["resource"]["organization"]["reference"].split("/")[-1]
            org_name = (
                OrganizationToName.objects.filter(organization_id=org_id)
                .values_list("name", flat=True)
                .first()
            )

            self.assertIn(name_search, org_name)

    def test_filter_by_distance_with_km(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        units = "km"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]
        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_with_mi(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 1
        units = "mi"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).miles, distance)

    def test_filter_by_distance_with_ft(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 5000
        units = "ft"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).feet, distance)

    def test_filter_by_distance_witout_units(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        near_query = f"{lat}|{lon}|{distance}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            position = (
                returned_location["position"]["longitude"],
                returned_location["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_none_nearby(self):
        lat = 64
        lon = 12
        distance = 30.5
        units = "km"
        near_query = f"{lon}|{lat}|{distance}|{units}"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]["entry"]), 0)

    def test_filter_by_practitioner_type(self):
        taxonomy = {"code": "152W00000X", "display_name": "Optometrist"}
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_type": taxonomy["display_name"]})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            practitioner_url = entry["resource"]["practitioner"]["reference"]
            returned_practitioner = self.client.get(practitioner_url).data
            taxonomies = [
                {
                    "code": tax["code"]["coding"][0]["code"],
                    "display_name": tax["code"]["coding"][0]["display"],
                }
                for tax in returned_practitioner["qualification"]
            ]

            self.assertIn(taxonomy, taxonomies)

    def test_filter_by_y_practitioner_type(self):
        taxonomy = {"code": "207PE0004X", "display_name": "Emergency Medical Services"}
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_type": "Emergency"})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            practitioner_url = entry["resource"]["practitioner"]["reference"]
            returned_practitioner = self.client.get(practitioner_url).data
            taxonomies = [
                {
                    "code": tax["code"]["coding"][0]["code"],
                    "display_name": tax["code"]["coding"][0]["display"],
                }
                for tax in returned_practitioner["qualification"]
            ]

            self.assertIn(taxonomy, taxonomies)

    def test_filter_by_organization_type(self):
        org_taxonomy = {"code": "261QE0800X", "display_name": "Endoscopy"}
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_type": org_taxonomy["display_name"]})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            organization_url = entry["resource"]["organization"]["reference"]
            returned_organization = self.client.get(organization_url).data
            # We are not currently exposing "qualification" at the Organization endpoint
            # taxonomies = [
            #    {
            #        "code": tax["code"]["coding"][0]["code"],
            #        "display_name": tax["code"]["coding"][0]["display"],
            #    }
            #    for tax in returned_organization["qualification"]
            # ]
            # self.assertIn(org_taxonomy, taxonomies)
            org_id = returned_organization["id"]
            org_taxonomies = [
                org.nucc_code.code
                for org in Organization.objects.get(
                    pk=org_id
                ).clinicalorganization.organizationtotaxonomy_set.all()
            ]
            self.assertIn(org_taxonomy["code"], org_taxonomies)

    def test_filter_by_location_city(self):
        url = reverse("fhir-practitionerrole-list")
        location_city = "Sunnyville"
        response = self.client.get(url, {"location_address_city": location_city})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            self.assertEqual(location_city, returned_location["address"]["city"])

    def test_filter_by_location_state(self):
        url = reverse("fhir-practitionerrole-list")
        location_state = "CA"
        response = self.client.get(url, {"location_address_state": location_state})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            self.assertEqual(location_state, returned_location["address"]["state"])

    def test_filter_by_location_zip_code(self):
        url = reverse("fhir-practitionerrole-list")
        location_zipcode = "90001"
        response = self.client.get(url, {"location_address_postalcode": location_zipcode})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_url = entry["resource"]["location"][0]["reference"]
            returned_location = self.client.get(location_url).data
            self.assertEqual(location_zipcode, returned_location["address"]["postalCode"])

    def test_list_filter_by_endpoint_connection_type(self):
        connection_type_id = "secure-email"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"endpoint_connection_type": connection_type_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        connection_types = []
        for entry in bundle["entry"]:
            for endpoint in entry["resource"]["endpoint"]:
                endpoint_url = endpoint["reference"]
                returned_endpoint = self.client.get(endpoint_url).data
                connection_types.append(returned_endpoint["connectionType"]["code"])
        self.assertIn(connection_type_id, connection_types)

    def test_list_filter_by_endpoint_payload_type(self):
        payload_type = "urn:ihe:pcc:xphr:2007"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"endpoint_payload_type": payload_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            payload_types = []
            for endpoint in entry["resource"]["endpoint"]:
                endpoint_url = endpoint["reference"]
                returned_organization = self.client.get(endpoint_url).data
                payload_types += [
                    pt["coding"][0]["code"] for pt in returned_organization["payloadType"]
                ]
            self.assertIn(payload_type, payload_types)

    # We don't have a concept of endpoint organizations at the moment
    # def test_list_filter_by_endpoint_organization_id(self):
    #    organization_id = self.organization_id
    #    url = reverse("fhir-practitionerrole-list")
    #    response = self.client.get(url, {"endpoint_organization_id": organization_id})
    #    self.assertEqual(response.status_code, status.HTTP_200_OK)
    #    assert_has_results(self, response)
    #
    #    bundle = response.data["results"]
    #
    #    for entry in bundle["entry"]:
    #        endpoint_url = entry["resource"]["endpoint"][0]["reference"]
    #        returned_endpoint = self.client.get(endpoint_url).data
    #        self.assertIn(organization_id, returned_endpoint["managingOrganization"])
    #
    # def test_list_filter_by_endpoint_organization_name(self):
    #    name_search = "Charlie Brown M.D."
    #    url = reverse("fhir-practitionerrole-list")
    #    response = self.client.get(url, {"endpoint_organization_name": name_search})
    #    self.assertEqual(response.status_code, status.HTTP_200_OK)
    #    assert_has_results(self, response)
    #
    #    for entry in response.data["results"]["entry"]:
    #        endpoint_url = entry["resource"]["endpoint"][0]["reference"]
    #        returned_endpoint = self.client.get(endpoint_url).data
    #        organization_url = returned_endpoint["managingOrganization"]["reference"]
    #        returned_organization = self.client.get(organization_url).data
    #        returned_organization_names = [returned_organization["name"]]
    #        if "alias" in returned_organization:
    #            returned_organization_names += returned_organization["alias"]
    #
    #        self.assertIn(name_search, returned_organization_names)

    def test_list_filter_by_specialty_code(self):
        url = reverse("fhir-practitionerrole-list")
        specialty_code = "777"
        response = self.client.get(url, {"specialty": specialty_code})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            self.assertEqual(specialty_code, entry["resource"]["specialty"][0]["coding"][0]["code"])

    # Retrieve tests
    def test_retrieve_nonexistent_uuid(self):
        url = reverse("fhir-practitionerrole-detail", args=["12300000-0000-0000-0000-000000000124"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_nonexistent_npi(self):
        url = reverse("fhir-practitionerrole-detail", args=["999999"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_pracitionerrole(self):
        id = "cad156c0-87fb-489b-bf5e-f15c95ee771e"
        url = reverse("fhir-practitionerrole-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))

    def test_list_filter_by_address_city(self):
        city_search = "Sunnyville"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_address_city": city_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            for entry in bundle["entry"]:
                self.assertEqual(1, len(entry["resource"]["location"]))
                location_url = entry["resource"]["location"][0]["reference"]
                returned_location = self.client.get(location_url).data
                self.assertEqual(city_search, returned_location["address"]["city"])

    def test_list_filter_by_address_state(self):
        state_search = "CA"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_address_state": state_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            for entry in bundle["entry"]:
                self.assertEqual(1, len(entry["resource"]["location"]))
                location_url = entry["resource"]["location"][0]["reference"]
                returned_location = self.client.get(location_url).data
                self.assertEqual(state_search, returned_location["address"]["state"])

    def test_list_filter_by_address_zip(self):
        zip_search = "90001"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_address_postalcode": zip_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            for entry in bundle["entry"]:
                self.assertEqual(1, len(entry["resource"]["location"]))
                location_url = entry["resource"]["location"][0]["reference"]
                returned_location = self.client.get(location_url).data
                self.assertEqual(zip_search, returned_location["address"]["postalCode"])

    def test_list_filter_by_address_zip_leading_zero(self):
        zip_search = "05555"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_address_postalcode": zip_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            for entry in bundle["entry"]:
                self.assertEqual(1, len(entry["resource"]["location"]))
                location_url = entry["resource"]["location"][0]["reference"]
                returned_location = self.client.get(location_url).data
                self.assertEqual(zip_search, returned_location["address"]["postalCode"])

    def test_list_filter_by_address_general_zip_leading_zero(self):
        address_line_1 = "404 Great Amazing Avenue"
        city = "San Diego"
        state = "CA"
        zip_code = "05555"
        address_search = " ".join([address_line_1, city, state, zip_code])
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            for entry in bundle["entry"]:
                self.assertEqual(1, len(entry["resource"]["location"]))
                location_url = entry["resource"]["location"][0]["reference"]
                returned_location = self.client.get(location_url).data
                self.assertEqual(zip_code, returned_location["address"]["postalCode"])
                self.assertEqual(state, returned_location["address"]["state"])
                self.assertEqual(city, returned_location["address"]["city"])
                self.assertIn(address_line_1, returned_location["address"]["line"])
