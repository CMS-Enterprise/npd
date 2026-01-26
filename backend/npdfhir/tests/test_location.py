from django.urls import reverse
from rest_framework import status

from geopy.distance import geodesic

from .api_test_case import APITestCase
from .fixtures.location import create_location
from .fixtures.organization import create_organization
from .helpers import (
    assert_fhir_response,
    assert_has_results,
    assert_pagination_limit,
    extract_resource_names,
    concat_address_string,
)


class LocationViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.orgs = [
            create_organization(name="Alpha Org", organization_type="283Q00000X"),
            create_organization(name="Beta Org"),
        ]

        cls.locs = [
            create_location(name="Main Clinic", organization=cls.orgs[0]),
            create_location(name="1ST CHOICE MEDICAL DISTRIBUTORS, LLC", organization=cls.orgs[0]),
            create_location(name="986 INFUSION PHARMACY #1 INC.", organization=cls.orgs[1]),
            create_location(name="A & A MEDICAL SUPPLY COMPANY", organization=cls.orgs[1]),
            create_location(
                id="3719c831-a4b7-4a7f-bb47-465a024384fc",
                name="ABACUS BUSINESS CORPORATION GROUP INC.",
                organization=cls.orgs[0],
                city="San Diego",
                state="CA",
                zipcode="55555",
                addr_line_1="404 Great Amazing Avenue",
                x=32.824056,
                y=-117.437397,
            ),
            create_location(
                id="7c7a433b-fca7-4fb2-9283-dc764fb0ed5c",
                name="ABBY D CENTER, INC.",
                organization=cls.orgs[1],
                city="Seattle",
                state="WA",
                zipcode="77777",
                addr_line_1="333 Grunge Blvd.",
                address_use="home",
                x=47.608597,
                y=-122.5046021,
            ),
            create_location(
                id="6df24407-ebe0-4f0b-9a75-bdfee486f0df",
                name="ABC DURABLE MEDICAL EQUIPMENT INC",
                organization=cls.orgs[0],
                city="St. Louis",
                state="MO",
                zipcode="89898",
                addr_line_1="66 Arch Lane",
                x=38.6219297,
                y=-90.182935,
            ),
            create_location(
                id="c1fc1ada-841a-4b92-9e8e-37f4d17b65d4",
                name="ABC HOME MEDICAL SUPPLY, INC.",
                organization=cls.orgs[0],
                city="St. Louis",
                state="MO",
                zipcode="65313",
                addr_line_1="City Museum Rd.",
                x=38.6336745,
                y=-90.2032725,
            ),
            create_location(
                id="b7517cc7-b406-4932-9856-6983ac4ec308",
                name="A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
                organization=cls.orgs[0],
                city="Ft. Lauderdale",
                state="FL",
                zipcode="43433",
                addr_line_1="789 Palmetto Road",
                x=26.1412097,
                y=-80.191004,
            ),
            create_location(
                name="A & B HEALTH CARE, INC.", organization=cls.orgs[0], x=None, y=None
            ),
            create_location(name="ABILENE HELPING HANDS INC", organization=cls.orgs[0]),
            create_location(name="ZEELAND COMMUNITY HOSPITAL", organization=cls.orgs[0]),
            create_location(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD", organization=cls.orgs[0]),
            create_location(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD", organization=cls.orgs[1]),
            create_location(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD", organization=cls.orgs[1]),
            create_location(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD", organization=cls.orgs[1]),
            create_location(name="YOUNGSTOWN ORTHOPAEDIC ASSOCIATES LTD", organization=cls.orgs[1]),
            create_location(name="YOUNG C. BAE, M.D."),
            create_location(name="YORKTOWN EMERGENCY MEDICAL SERVICE"),
            create_location(name="YODORINCMISSIONPLAZAPHARMACY", organization=cls.orgs[0]),
            create_location(name="YOAKUM COMMUNITY HOSPITAL", organization=cls.orgs[0]),
            create_location(
                name="FROEDTERT MEMORIAL LUTHERAN HOSPITAL, INC.", organization=cls.orgs[1]
            ),
            create_location(name="AMBER ENTERPRISES INC.", organization=cls.orgs[0]),
            create_location(name="COUNTY OF KOOCHICHING", organization=cls.orgs[0]),
            create_location(name="OCEAN HOME HEALTH SUPPLY, LLC", organization=cls.orgs[0]),
            create_location(name="PULMONARY MANAGEMENT, INC.", organization=cls.orgs[0]),
            create_location(name="MEDICATION MANAGEMENT CENTER, LLC.", organization=cls.orgs[1]),
            create_location(name="HENDRICKS COUNTY HOSPITAL", organization=cls.orgs[1]),
            create_location(name="BAY AREA REHABILITATION MEDICAL GROUP", organization=cls.orgs[1]),
            create_location(name="PROHAB REHABILITATION SERVICES, INC.", organization=cls.orgs[1]),
        ]
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

        sorted_names = [
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
        ]

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

        sorted_names = [
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

        self.assertEqual(
            names,
            sorted_names,
            f"Expected locations list sorted by name in descending but got {names}\n Sorted: {sorted_names}",
        )

    def test_list_in_order_by_address(self):
        url = reverse("fhir-location-list")
        response = self.client.get(url, {"_sort": "address_full,name"})
        assert_fhir_response(self, response)

        # Extract names
        # Note: have to normalize the names to have python sorting match sql
        names = extract_resource_names(response)

        # Names correspond to following addresses
        # 10000 W Bluemound Rd, Wauwatosa, WI 53226
        # 10004 S 152nd St, Omaha, NE 68138
        # 1000 5th St, International Falls, MN 56649
        # 1000 Airport Rd, Lakewood, NJ 8701
        # 1000 E Center St, Kingsport, TN 37660
        # 1000 E Main St, Danville, IN 46122
        # 1000 Greenley Rd, Sonora, CA 95370
        # 1000 Regency Ct, Toledo, OH 43623

        sorted_names = [
            "1ST CHOICE MEDICAL DISTRIBUTORS, LLC",
            "986 INFUSION PHARMACY #1 INC.",
            "A & A MEDICAL SUPPLY COMPANY",
            "A & B HEALTH CARE, INC.",
            "ABILENE HELPING HANDS INC",
            "AMBER ENTERPRISES INC.",
            "BAY AREA REHABILITATION MEDICAL GROUP",
            "COUNTY OF KOOCHICHING",
            "FROEDTERT MEMORIAL LUTHERAN HOSPITAL, INC.",
            "HENDRICKS COUNTY HOSPITAL",
        ]

        self.assertEqual(
            names,
            sorted_names,
            f"Expected locations list sorted by address ascending but got {names}\n Sorted: {sorted_names}",
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
        name = self.locs[0].name

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
            self.assertEqual(str(self.orgs[0].id), parsed_org_id)

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
        id = self.locs[0].id
        url = reverse("fhir-location-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))
