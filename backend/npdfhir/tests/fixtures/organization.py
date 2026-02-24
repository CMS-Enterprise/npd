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
)

from typing import TypeDict, List
from practitioner import DefaultIndividual, DefaultNPI, DefaultOtherIDs
from address import DefaultAddress
from endpoint import DefaultEndpointInstance


class DefaultLocation(TypeDict):
    address: DefaultAddress
    endpoint_instance: DefaultEndpointInstance
    name: str = "Location A"
    id: uuid = None


class DefaultOrganization:
    def __init__(
        self,
        npi: DefaultNPI,
        authorized_official: DefaultIndividual,
        other_ids: DefaultOtherIDs,
        locations: list[DefaultLocation],
        id: uuid = None,
        parent_id: uuid = None,
        names: List[str] = ["Organization ABC"],
        taxonomies: list[str] = ["193200000X"],
        is_clinical: bool = True,
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.parent_id = parent_id
        if is_clinical and npi is None:
            self.npi = DefaultNPI()
        self.names = names
        self.taxonomies = taxonomies
        if authorized_official is None:
            authorized_official = DefaultIndividual()
        self.authorized_official = authorized_official
        if not other_ids:
            other_ids = [DefaultOtherIDs()]
        self.other_ids = other_ids
        if not locations:
            locations = [DefaultLocation()]
        self.locations = locations
        self.create_if_not_exists()

    def create_if_not_exists(self):
        organization = Organization.objects.filter(id=self.id)
        if organization.exists():
            self.organization = organization.first()
        else:
            organization = Organization.objects.create(
                id=self.id, parent_id=self.parent_id, authorized_official=self.authorized_official
            )
            for i, name in enumerate(self.names):
                OrganizationToName.objects.create(
                    organization=organization,
                    name=name,
                    is_primary=i == 0,
                )

            for address in self.locations:
                OrganizationToAddress.objects.create(
                    organization=organization, address=address, address_use_id=2
                )

            if self.is_clinical:
                clinical_organization = ClinicalOrganization.objects.create(
                    organization=organization, npi=self.npi
                )

                for id in self.other_ids:
                    OrganizationToOtherId.objects.create(
                        npi=clinical_organization,
                        other_id=id.other_id_name,
                        other_id_type=id.other_id_type,
                        state_code__abbreviation=id.state,
                    )
                for taxonomy in self.taxonomies:
                    OrganizationToTaxonomy.objects.create(
                        npi=clinical_organization, nucc_code_id=taxonomy
                    )
                self.add_locations()

        return organization

    def add_locations(self, locations: List[DefaultLocation]):
        if self.locations is None:
            self.locations = locations
        else:
            self.locations += locations
        for address in self.locations:
            location = Location.objects.create(
                id=address.id,
                name=address.name,
                organization_id=self.id,
                address=address.address,
                active=True,
            )
            LocationToEndpointInstance.objects.create(
                location_id=location.id, endpoint_instance=address.endpoint_instance
            )
