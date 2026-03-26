import uuid

from ...models import (
    ClinicalOrganization,
    Organization,
    OrganizationToName,
    OrganizationToOtherId,
    OrganizationToTaxonomy,
    OrganizationToAddress,
    Location,
    LocationToEndpointInstance,
    FipsState,
)

from typing import List
from .practitioner import DefaultIndividual, DefaultNPI, DefaultOtherID
from .address import DefaultAddress
from .endpoint import DefaultEndpointInstance


class DefaultLocation:
    def __init__(
        self,
        address: DefaultAddress = None,
        endpoint_instance: DefaultEndpointInstance = None,
        name: str = "Location A",
        id: uuid = None,
        has_endpoint: bool = True,
    ):
        if address is None:
            address = DefaultAddress()
        self.address = address
        if has_endpoint and endpoint_instance is None:
            endpoint_instance = DefaultEndpointInstance()
        self.endpoint_instance = endpoint_instance
        self.name = name
        if id is None:
            id = uuid.uuid4()
        self.id = id
        self.has_endpoint = has_endpoint


class DefaultOrganization:
    def __init__(
        self,
        npi: DefaultNPI = None,
        authorized_official: DefaultIndividual = None,
        other_ids: List[DefaultOtherID] = None,
        locations: List[DefaultLocation] = None,
        id: uuid = None,
        parent_id: uuid = None,
        names: List[str] = ["Organization ABC"],
        taxonomies: list[str] = ["193200000X"],
        is_clinical: bool = True,
        has_locations: bool = True,
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.parent_id = parent_id
        if is_clinical:
            if npi is None:
                self.npi = DefaultNPI()
            else:
                self.npi = npi
        self.names = names
        self.taxonomies = taxonomies
        if authorized_official is None:
            authorized_official = DefaultIndividual()
        self.authorized_official = authorized_official
        if not other_ids:
            other_ids = [DefaultOtherID()]
        self.other_ids = other_ids
        if has_locations and not locations:
            locations = [DefaultLocation()]
        self.locations = locations
        self.is_clinical = is_clinical
        self.has_locations = has_locations
        self.create_if_not_exists()

    def create_if_not_exists(self):
        organization = Organization.objects.filter(id=self.id)
        if organization.exists():
            self.organization = organization.first()
        else:
            organization = Organization.objects.create(
                id=self.id,
                parent_id=self.parent_id,
                authorized_official_id=self.authorized_official.id,
            )
            for i, name in enumerate(self.names):
                OrganizationToName.objects.create(
                    organization=organization,
                    name=name,
                    is_primary=i == 0,
                )

            if self.is_clinical:
                clinical_organization = ClinicalOrganization.objects.create(
                    organization=organization, npi=self.npi.npi
                )

                for id in self.other_ids:
                    state_code = FipsState.objects.filter(abbreviation=id.state).first()
                    OrganizationToOtherId.objects.create(
                        npi=clinical_organization,
                        other_id=id.other_id,
                        other_id_type_id=id.other_id_type,
                        state_code=state_code,
                    )
                for taxonomy in self.taxonomies:
                    OrganizationToTaxonomy.objects.create(
                        npi=clinical_organization, nucc_code_id=taxonomy
                    )
                self.add_locations()

        return organization

    def add_locations(self, locations: List[DefaultLocation] = []):
        if self.locations is None:
            self.locations = locations
        else:
            self.locations += locations
        for location in self.locations:
            if not Location.objects.filter(id=location.id).exists():
                OrganizationToAddress.objects.create(
                    address_id=location.address.id,
                    organization_id=self.id,
                    address_use_id=location.address.address_use_id,
                )
                Location.objects.create(
                    id=location.id,
                    name=location.name,
                    organization_id=self.id,
                    address=location.address.address,
                    active=True,
                )
                if location.has_endpoint:
                    LocationToEndpointInstance.objects.create(
                        location_id=location.id, endpoint_instance_id=location.endpoint_instance.id
                    )
