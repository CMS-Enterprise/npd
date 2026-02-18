import uuid

from ...models import (
    ClinicalOrganization,
    Organization,
    OrganizationToName,
    OrganizationToOtherId,
    OrganizationToTaxonomy,
    OrganizationToAddress,
    Location,
)

from typing import TypeDict, List
from practitioner import DefaultIndividual, DefaultNPI, DefaultOtherIDs
from practitioner import DefaultAddress


class DefaultLocation(TypeDict):
    address: DefaultAddress
    name: str = "Location A"
    id: uuid = None


class DefaultOrganization:
    def __init__(
        self,
        npi: DefaultNPI,
        authorized_official: DefaultIndividual,
        other_ids: DefaultOtherIDs,
        locations: List[DefaultLocation],
        id: uuid = None,
        names: List[str] = ["ABC Organization"],
        taxonomies: list[str] = ["193200000X"],
        is_clinical: bool = True,
    ):
        if self.id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        if is_clinical and npi is None:
            self.npi = npi.create_if_not_exists()
        self.names = names
        self.taxonomies = taxonomies
        self.authorized_official = authorized_official.create_if_not_exists()
        self.other_ids = other_ids
        self.locations = [location.create_if_not_exists() for location in locations]

    def create_if_not_exists(self):
        organization = Organization.objects.filter(id=self.id)
        if organization.exists():
            self.organization = organization
        else:
            organization = Organization.objects.create(
                id=self.id, authorized_official=self.authorized_official
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

                for address in self.locations:
                    Location.objects.create(
                        id=id,
                        name=name,
                        organization=organization,
                        address=address,
                        active=True,
                    )

            return organization
