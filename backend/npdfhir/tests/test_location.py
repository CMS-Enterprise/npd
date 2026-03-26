from django.urls import reverse
from rest_framework import status

from geopy.distance import geodesic

from .api_test_case import APITestCase
from .fixtures.address import DefaultAddress
from .fixtures.organization import DefaultOrganization, DefaultLocation
from .fixtures.practitioner import DefaultNPI, DefaultOtherID
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
    concat_address_string,
)
from ..models import OrganizationView


class LocationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # Generate test location data for address filtering
        locations = [
            {
                "id": "3719c831-a4b7-4a7f-bb47-465a024384fc",
                "address": {
                    "city": "San Diego",
                    "state": "CA",
                    "zip_code": "55555",
                    "line_1": "404 Great Amazing Avenue",
                    "x": 32.824056,
                    "y": -117.437397,
                },
            },
            {
                "id": "7c7a433b-fca7-4fb2-9283-dc764fb0ed5c",
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
                "address": {
                    "city": "St. Louis",
                    "state": "MO",
                    "zip_code": "05313",
                    "line_1": "City Museum Rd.",
                    "x": 38.6336745,
                    "y": -90.2032725,
                },
            },
            {
                "id": "b7517cc7-b406-4932-9856-6983ac4ec308",
                "address": {
                    "city": "Ft. Lauderdale",
                    "state": "FL",
                    "zip_code": "43433",
                    "line_1": "789 Palmetto Road",
                    "x": 26.1412097,
                    "y": -80.191004,
                },
            },
        ]
        for location in locations:
            address = location.copy()["address"]
            location.pop("address", None)
            DefaultOrganization(
                locations=[DefaultLocation(id=location["id"], address=DefaultAddress(**address))]
            )

        # Generate test location data for a different address use (home)
        DefaultOrganization(locations=[DefaultLocation(address=DefaultAddress(address_use_id=1))])

        # Generate test location data for alpha sorting
        cls.names_to_sort = [
            "1ST CHOICE MEDICAL DISTRIBUTORS, LLC",
            "986 INFUSION PHARMACY #1 INC.",
            "A & A MEDICAL SUPPLY COMPANY",
            "ABACUS BUSINESS CORPORATION GROUP INC.",
            "ABBY D CENTER, INC.",
            "ABC DURABLE MEDICAL EQUIPMENT INC",
            "ABC HOME MEDICAL SUPPLY, INC.",
            "A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
            "A & B HEALTH CARE, INC.",
            "ABILENE HELPING HANDS INC",
            "ZEELAND COMMUNITY HOSPITAL",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD",
            "YOUNG C. BAE, M.D.",
            "YORKTOWN EMERGENCY MEDICAL SERVICE",
            "YODORINCMISSIONPLAZAPHARMACY",
            "YOAKUM COMMUNITY HOSPITAL",
        ]
        for name in cls.names_to_sort:
            DefaultOrganization(locations=[DefaultLocation(name=name)])

        # Generate test data for retrieving specific Location
        DefaultOrganization(locations=[DefaultLocation(id="1d5d7925-d205-4dbc-be31-5a339c9fb9af")])

        # Generate test data for testing organization type filtering
        DefaultOrganization(id="62564fd9-072e-416e-a197-7cb512ce0433", taxonomies=["283Q00000X"])

        # Generate test data for testing organization name filtering
        DefaultOrganization(names=["Filter Org"])

        # Generate test data for testing organization identifier filtering
        DefaultOrganization(npi=DefaultNPI(npi=1000000001))
        DefaultOrganization(other_ids=[DefaultOtherID(other_id=1000000001)])

        OrganizationView.refresh_materialized_view()

        return super().setUpTestData()

    # Basic tests
    def test_list_default(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)
        assert_has_results(self, response)

    # Sorting tests
    def test_list_in_default_order(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url)
        assert_fhir_response(self, response)

        # Extract names
        names = extract_resource_names(response)

        sorted_names = self.names_to_sort[0:10]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected fhir locations sorted by name but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_descending_order(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"_sort": "-name"})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        sorted_names = self.names_to_sort[10:]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected locations list sorted by name in descending but got {names}\n Sorted: {sorted_names}",
        )

    # Pagination tests
    def test_list_with_custom_page_size(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"page_size": 2})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLessEqual(len(response.data["results"]["entry"]), 2)

    def test_list_with_greater_than_max_page_size(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"page_size": 1001})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_pagination_limit(self, response)

    # Filter tests
    def test_list_filter_by_name(self):
        name = self.names_to_sort[0]

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"name": name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)
            self.assertIn(name, location_entry["name"])

    def test_list_filter_by_name_partial(self):
        name = "ABC"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"name": name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)
            self.assertIn(name, location_entry["name"])

    def test_list_filter_by_name_whole(self):
        name = "ABC HOME MEDICAL SUPPLY, INC."

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"name": name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)
            self.assertIn(name, location_entry["name"])
            self.assertNotIn("ABC DURABLE MEDICAL EQUIPMENT INC", location_entry["name"])

    def test_list_filter_by_y_name(self):
        name = "SUPPLY"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"name": name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)
            self.assertIn(name, location_entry["name"])

    def test_filter_by_org_type(self):
        nucc_type = "283Q00000X"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"organization_type": nucc_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            parsed_org_id = location_entry["managingOrganization"]["reference"].split("/")[-1]
            # Assert that correct org was referenced by org type
            self.assertEqual("62564fd9-072e-416e-a197-7cb512ce0433", parsed_org_id)

    def test_filter_by_org_name(self):
        org_name = "Filter Org"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"organization_name": org_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            org_names = []
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            organizationResponse = self.client.get(
                location_entry["managingOrganization"]["reference"]
            )
            organization = organizationResponse.data
            if "alias" in organization.keys():
                alias = organization["alias"]
            else:
                alias = []
            for name in [organization["name"]] + alias:
                org_names.append(name)
            self.assertIn(org_name, org_names)

    def test_filter_by_org_npi(self):
        org_npi = "1000000001"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"organization_identifier": f"NPI|{org_npi}"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        self.assertEqual(1, len(bundle["entry"]))

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            organizationResponse = self.client.get(
                location_entry["managingOrganization"]["reference"]
            )
            organization = organizationResponse.data
            npi_response = [
                identifier["value"]
                for identifier in organization["identifier"]
                if identifier["type"]["coding"][0]["code"] == "NPI"
            ]
            self.assertIn(org_npi, npi_response)

    def test_filter_by_org_identifier(self):
        org_other_id = "1000000001"

        url = reverse("fhir-location-list")
        response = self.client.get(url, {"organization_identifier": org_other_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        self.assertEqual(2, len(bundle["entry"]))

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]
            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            organizationResponse = self.client.get(
                location_entry["managingOrganization"]["reference"]
            )
            organization = organizationResponse.data
            identifiers = [identifier["value"] for identifier in organization["identifier"]]
            self.assertIn(org_other_id, identifiers)

    def test_list_filter_by_address(self):
        address_search = "Amazing Avenue"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            address_string = concat_address_string(location_entry["address"])
            self.assertIn(address_search, address_string)

    def test_list_filter_by_address_leading_zero(self):
        address_search = "05313"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address": address_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            address_string = concat_address_string(location_entry["address"])
            self.assertIn(address_search, address_string)

    def test_list_filter_by_address_city(self):
        city_search = "St. Louis"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_city": city_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            self.assertIn(city_search, location_entry["address"]["city"])

    def test_list_filter_by_address_state(self):
        state_search = "MO"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_state": state_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            self.assertIn(state_search, location_entry["address"]["state"])

    def test_list_filter_by_address_postalcode(self):
        zip_search = "55555"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_postalcode": zip_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            self.assertIn(zip_search, location_entry["address"]["postalCode"])

    def test_list_filter_by_address_postalcode_leading_zero(self):
        zip_search = "05313"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_postalcode": zip_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            self.assertIn(zip_search, location_entry["address"]["postalCode"])

    def test_list_filter_by_address_use(self):
        use_search = "home"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"address_use": use_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "Location")
            self.assertIn("id", location_entry)
            self.assertIn("status", location_entry)
            self.assertIn("managingOrganization", location_entry)
            self.assertIn("address", location_entry)
            self.assertIn("name", location_entry)

            self.assertIn(use_search, location_entry["address"]["use"])

    def test_filter_by_distance_with_km(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        units = "km"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            position = (
                entry["resource"]["position"]["longitude"],
                entry["resource"]["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_with_mi(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 1
        units = "mi"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            position = (
                entry["resource"]["position"]["longitude"],
                entry["resource"]["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).miles, distance)

    def test_filter_by_distance_with_ft(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 5000
        units = "ft"
        near_query = f"{lat}|{lon}|{distance}|{units}"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            position = (
                entry["resource"]["position"]["longitude"],
                entry["resource"]["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).feet, distance)

    def test_filter_by_distance_witout_units(self):
        lat = -90.194315
        lon = 38.629267
        location = (lon, lat)
        distance = 3
        near_query = f"{lat}|{lon}|{distance}"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            position = (
                entry["resource"]["position"]["longitude"],
                entry["resource"]["position"]["latitude"],
            )
            self.assertLessEqual(geodesic(location, position).km, distance)

    def test_filter_by_distance_none_nearby(self):
        lat = 64
        lon = 12
        distance = 30.5
        units = "km"
        near_query = f"{lon}|{lat}|{distance}|{units}"
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"near": near_query})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]["entry"]), 0)

    # Retrieve tests
    def test_retrieve_nonexistent(self):
        url = reverse("fhir-location-detail", args=["00000000-0000-0000-0000-000000000000"])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_retrieve_single_location(self):
        id = "1d5d7925-d205-4dbc-be31-5a339c9fb9af"
        url = reverse("fhir-location-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))
