from .practitioner import DefaultPractitioner
from .organization import DefaultOrganization, DefaultLocation
from ...models import ProviderToLocation, Location, ProviderToOrganization
import uuid


class DefaultPractitionerRole:
    def __init__(
        self,
        id: uuid = None,
        practitioner: DefaultPractitioner = None,
        organization: DefaultOrganization = None,
        location: DefaultLocation = None,
        relationship_type_id: int = 1,
        specialty: str = 10,
        active: bool = True,
    ):
        if not id:
            id = uuid.uuid4()
        self.id = id
        if not practitioner:
            practitioner = DefaultPractitioner()
        self.practitioner = practitioner
        if not location:
            location = DefaultLocation()
        self.location = location
        if not organization:
            organization = DefaultOrganization(locations=[location])
        self.organization = organization
        self.relationship_type_id = relationship_type_id
        self.active = active
        self.specialty = specialty
        self.create_if_not_exists()

    def create_if_not_exists(self):
        if not Location.objects.filter(id=self.location.id).exists():
            self.organization.add_locations([self.location])
        pto = ProviderToOrganization.objects.filter(
            organization_id=self.organization.id, individual_id=self.practitioner.individual.id
        )
        if pto.exists():
            pto = pto.first()
        else:
            pto = ProviderToOrganization.objects.create(
                id=uuid.uuid4(),
                organization_id=self.organization.id,
                individual_id=self.practitioner.individual.id,
                relationship_type_id=self.relationship_type_id,
                active=self.active,
            )
        practitioner_role = ProviderToLocation.objects.filter(
            location_id=self.location.id, provider_to_organization_id=pto.id
        )
        if practitioner_role.exists():
            self.practitioner_role = practitioner_role.first()
        else:
            practitioner_role = ProviderToLocation.objects.create(
                id=self.id,
                provider_to_organization_id=pto.id,
                location_id=self.location.id,
                active=self.active,
                specialty_id=self.specialty,
            )
        self.practitioner_role = practitioner_role
        return self.practitioner_role
