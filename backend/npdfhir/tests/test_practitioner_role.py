import math
import uuid

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
    Nucc,
    EndpointInstanceToPayload,
    OrganizationToName,
    Provider,
    ProviderToOrganization,
    ProviderToLocation,
    ProviderToTaxonomy,
    PayloadType,
    Location,
    LocationToEndpointInstance,
    IndividualToName
)


from .fixtures.organization import create_organization
from .fixtures.endpoint import create_endpoint
from .fixtures.location import create_location
from .fixtures.practitioner import (
    create_practitioner,
    create_full_practitionerrole,
    _ensure_relationship_type,
    _ensure_provider_role,
)


class PractitionerRoleViewSetTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        # (location_name, uuid)
        cls.orgs = [
            "A BEAUTIFUL SMILE DENTISTRY, L.L.C.",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADIRONDACK MEDICAL HEALTH CARE ASSOCIATES PLLC",
            "ADR LLC",
            "ADR LLC",
            "ADR LLC",
            "ADR LLC",
        ]
        cls.locations = [
            create_location(
                id="3719c831-a4b7-4a7f-bb47-465a024384fc",
                name="ABACUS BUSINESS CORPORATION GROUP INC.",
                organization_name=cls.orgs[0],
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
                organization_name=cls.orgs[1],
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
                organization_name=cls.orgs[0],
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
                organization_name=cls.orgs[0],
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
                organization_name=cls.orgs[0],
                city="Ft. Lauderdale",
                state="FL",
                zipcode="43433",
                addr_line_1="789 Palmetto Road",
                x=26.1412097,
                y=-80.1910040,
            ),
        ]

        locs = cls.locations + cls.locations
        cls.roles = []

        for i, loc_name in enumerate(cls.orgs):
            # You can vary practitioner data a bit to avoid collisions
            first = f"Test{i}"
            last = f"Practitioner{i}"
            npi = 1000000000 + i

            location = locs[i]

            role = create_full_practitionerrole(
                first_name=first,
                last_name=last,
                gender="M" if i % 2 == 0 else "F",
                npi_value=npi,
                location_id=location.id,
                org_name=cls.orgs[math.floor(i / 2)],
                role_display="Clinician",
                role_code="MD",
                nucc_types=["101200000X"],
            )

            cls.roles.append(role)

        cls.first_prac_id = cls.roles[0].id

        cls.roles_with_params = []

        # Practitioner with taxonomy (practitioner_type) set separately
        provider = create_practitioner(
            first_name="Charlie",
            last_name="Brown",
            gender="M",
            npi_value=3000000001,
        )
        taxonomy_code = Nucc.objects.first()  # pick any Nucc code for practitioner_type
        if taxonomy_code:
            from ..models import ProviderToTaxonomy

            ProviderToTaxonomy.objects.create(
                id=uuid.uuid4(),
                npi=provider,
                nucc_code=taxonomy_code,
            )

        # Create organization and location
        cls.org_name = "Sunshine Health"
        cls.orgs.append(cls.org_name)
        org = create_organization(
            name=cls.org_name, organization_type=taxonomy_code.code if taxonomy_code else None
        )
        loc = create_location(
            organization=org,
            name="Sunshine Clinic",
            city="Sunnyville",
            state="CA",
            zipcode="90001",
            addr_line_1="123 Sunshine St",
        )

        role_code = "MD"
        role_display = "Clinician"
        # Create ProviderToOrganization & ProviderToLocation via full_practitionerrole
        # Ensure relationship + role codes exist
        rel_type = _ensure_relationship_type()
        _ensure_provider_role(role_code, role_display)

        pto_org = ProviderToOrganization.objects.create(
            id=uuid.uuid4(),
            individual=provider,  # special FK uses Provider.individual_id
            organization=org,
            relationship_type=rel_type,
            active=True,
        )

        payload = PayloadType.objects.create(
            id="application/fhir+json",
            value="FHIR JSON",
        )

        # Add endpoint
        ep = create_endpoint(
            organization=org,
            url="https://sunshine.example.org/fhir",
            name="Sunshine FHIR Endpoint",
        )

        LocationToEndpointInstance.objects.create(
            location=loc,
            endpoint_instance=ep.endpoint_instance,
        )

        EndpointInstanceToPayload.objects.create(
            endpoint_instance=ep.endpoint_instance,
            payload_type=payload,
        )

        pr = ProviderToLocation.objects.create(
            id=uuid.uuid4(),
            provider_to_organization=pto_org,
            location=loc,
            provider_role_code=role_code,
            other_endpoint=ep,
            specialty_id=7777,
            active=True,
        )
        cls.roles_with_params.append(pr)

        # Save references for tests
        cls.provider = provider
        cls.organization = org
        cls.location = loc
        cls.endpoint = ep
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

    # Filter tests
    def test_list_filter_by_name(self):
        sample_name = "Charlie"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_name": sample_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            #Query the practitioner names based on the returned id
            practitioner_id = entry["resource"]["practitioner"]["reference"].split("/")[-1]
            provider = Provider.objects.select_related("individual").get(
                individual_id=practitioner_id
            )

            name_objects = IndividualToName.objects.filter(individual=provider.individual).all()

            #Save if the search matches an individual name associated with a provider
            match_conditions = []

            for name in name_objects:
                name_string = ""
                name_string += f"{name.prefix or ""}"
                name_string += f"{name.first_name or ""} {name.middle_name or ""}"
                name_string += f"{name.last_name or ""} {name.suffix or ""}"

                match_conditions.append(sample_name in name_string)

            #Make sure that the provider has any individual name that matches
            self.assertTrue(any(match_conditions))

    def test_list_filter_by_practitioner_gender(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_gender": "Female"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            #Query the practitioner individual based on the returned id
            practitioner_id = entry["resource"]["practitioner"]["reference"].split("/")[-1]
            provider = Provider.objects.select_related("individual").get(
                individual_id=practitioner_id
            )

            self.assertEqual('F', provider.individual.gender)

    def test_list_filter_by_organization_name(self):
        name_search = "MEDICAL"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_name": name_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        for entry in response.data["results"]["entry"]:
            #Query the practitioner names based on the returned id
            org_id = entry["resource"]["organization"]["reference"].split("/")[-1]
            org_name = (
                OrganizationToName.objects
                .filter(organization_id=org_id)
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
        id = self.first_prac_id
        url = reverse("fhir-practitionerrole-detail", args=[id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["id"], str(id))

    def test_filter_by_practitioner_type(self):
        taxonomy = ProviderToTaxonomy.objects.filter(npi=self.provider).first()
        self.assertIsNotNone(taxonomy)
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"practitioner_type": str(taxonomy.nucc_code.code)})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

    def test_filter_by_organization_type(self):
        org_taxonomy = Nucc.objects.first()
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"organization_type": str(org_taxonomy.pk)})
        self.assertEqual(response.status_code, 200)
        assert_has_results(self, response)

    def test_filter_by_location_city_state_zip(self):
        url = reverse("fhir-practitionerrole-list")
        for param, value in {
            "location_city": self.location.address.address_us.city_name,
            "location_state": self.location.address.address_us.state_code.abbreviation,
            "location_zip_code": self.location.address.address_us.zipcode,
        }.items():
            resp = self.client.get(url, {param: value})
            self.assertEqual(resp.status_code, 200)
            assert_has_results(self, resp)

    def test_list_filter_by_address_city(self):
        city_search = "Sunnyville"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_city": city_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_id = entry["resource"]["location"][0]["reference"].split("/")[-1]
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            location_obj = Location.objects.get(pk=location_id)

            self.assertEqual(city_search, location_obj.address.address_us.city_name)

    def test_list_filter_by_address_state(self):
        state_search = "CA"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_state": state_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_id = entry["resource"]["location"][0]["reference"].split("/")[-1]
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            location_obj = Location.objects.get(pk=location_id)

            self.assertEqual(state_search, location_obj.address.address_us.state_code.abbreviation)

    def test_list_filter_by_address_zip(self):
        zip_search = "90001"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"location_zip_code": zip_search})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            location_id = entry["resource"]["location"][0]["reference"].split("/")[-1]
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            location_obj = Location.objects.get(pk=location_id)

            self.assertEqual(zip_search, location_obj.address.address_us.zipcode)

    def test_list_filter_by_endpoint_connection_type(self):
        connection_type_id = self.endpoint.endpoint_instance.endpoint_connection_type.id
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"endpoint_connection_type": connection_type_id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            # print(entry["resource"])#['location'][0]['reference'].split('/')[-1])
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

            # location_obj = Location.objects.get(pk=location_id)

    def test_list_filter_by_endpoint_payload_type(self):
        payload_type = "application/fhir+json"
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"endpoint_payload_type": payload_type})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

    def test_list_filter_by_endpoint_organization_id(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"filter_endpoint_organization_id": self.organization.id})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]
        # print(response.data)

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

    def test_list_filter_by_endpoint_organization_name(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"filter_endpoint_organization_name": self.org_name})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)

    def test_list_filter_by_specialty_code(self):
        url = reverse("fhir-practitionerrole-list")
        response = self.client.get(url, {"specialty": "7777"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        assert_has_results(self, response)

        bundle = response.data["results"]

        self.assertEqual(response.data["count"], 1)
        for entry in bundle["entry"]:
            self.assertIn("resource", entry)
            location_entry = entry["resource"]

            self.assertEqual(location_entry["resourceType"], "PractitionerRole")
            self.assertIn("id", location_entry)
            self.assertIn("active", location_entry)
