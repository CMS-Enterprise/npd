import datetime
import random
import uuid

from ...models import (
    FhirAddressUse,
    FipsState,
    Individual,
    IndividualToAddress,
    IndividualToName,
    Npi,
    Nucc,
    OtherIdType,
    Provider,
    ProviderRole,
    ProviderToLocation,
    ProviderToOrganization,
    ProviderToOtherId,
    ProviderToTaxonomy,
    RelationshipType,
)
from .location import create_location
from .organization import create_organization
from .utils import _ensure_name_use


def _ensure_provider_role(code="PRV", display="Provider Role"):
    return ProviderRole.objects.get_or_create(
        code=code,
        defaults={
            "system": "http://hl7.org/fhir/practitionerrole",
            "display": display,
        },
    )[0]


def _ensure_relationship_type():
    """
    Retrieve an existing relationship_type inserted by Flyway.
    Default: 'assigning' (id=2)
    """
    try:
        return RelationshipType.objects.get(value="assigning")
    except RelationshipType.DoesNotExist:
        # If Flyway hasn’t run (edge/dev case), create one safely
        return RelationshipType.objects.create(value="assigning")


def create_practitioner(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    birth_date=datetime.date(1990, 1, 1),
    npi_value=None,
    other_id=None,
    other_id_type=None,
    state=None,
    practitioner_types=None,
    location=None,
    address_use="work",
):
    """
    Creates an Individual, Name (via IndividualToName), Npi, Provider.
    """
    individual = Individual.objects.create(
        id=uuid.uuid4(),
        gender=gender,
        birth_date=birth_date,
    )

    IndividualToName.objects.create(
        individual=individual,
        first_name=first_name,
        last_name=last_name,
        name_use=_ensure_name_use(),
    )

    if location:
        use = FhirAddressUse.objects.get(value=address_use)

        IndividualToAddress.objects.create(
            individual=individual, address=location.address, address_use=use
        )

    npi_value = npi_value or random.randint(1000000000, 9999999999)

    npi = Npi.objects.create(
        npi=npi_value,
        entity_type_code=1,
        enumeration_date=datetime.date(2000, 1, 1),
        last_update_date=datetime.date(2020, 1, 1),
    )

    provider = Provider.objects.create(
        npi=npi,
        individual=individual,
    )

    if other_id:
        other_id_type = OtherIdType.objects.get(value=(other_id_type or "OTHER"))
        fips_code = FipsState.objects.get(abbreviation=(state or "NY"))
        ProviderToOtherId.objects.create(
            npi=provider,
            other_id=other_id,
            other_id_type=other_id_type,
            state_code=fips_code,
            issuer="TEST",
        )

    if practitioner_types:
        for type in practitioner_types:
            code = Nucc.objects.get(pk=type)

            ProviderToTaxonomy.objects.create(npi=provider, nucc_code=code, id=uuid.uuid4())

        # display name
        # Nucc

    return provider


def create_full_practitionerrole(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    npi_value=None,
    org_name="Test Org",
    location_id=None,
    role_code="PRV",
    role_display="Provider Role",
    nucc_types=None
):
    """
    Creates:
        Practitioner (Provider)
        Organization
        Location
        ProviderToOrganization
        ProviderToLocation
    """
    provider = create_practitioner(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        npi_value=npi_value,
        practitioner_types=nucc_types
    )

    org = create_organization(name=org_name)
    if location_id is None:
        loc = create_location()
        location_id = loc.id

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

    pr = ProviderToLocation.objects.create(
        id=uuid.uuid4(),
        provider_to_organization=pto_org,
        location_id=location_id,
        provider_role_code=role_code,
        active=True,
    )

    return pr
