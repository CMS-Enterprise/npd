import datetime
import uuid

from ...models import (
    ClinicalOrganization,
    Individual,
    IndividualToName,
    LegalEntity,
    Npi,
    Nucc,
    Organization,
    OrganizationToName,
    OrganizationToOtherId,
    OrganizationToTaxonomy,
)
from .utils import _ensure_name_use


def create_legal_entity(dba_name="Sample Legal Entity"):
    legal_entity = LegalEntity.objects.create(ein_id=uuid.uuid4(), dba_name=dba_name)

    return legal_entity


def create_organization(
    id=None,
    name="Test Org",
    parent_id=None,
    authorized_official_first_name="Alice",
    authorized_official_last_name="Smith",
    legal_entity=None,
    other_id_type=None,
    other_id_value=None,
    npi_value=None,
    other_id_name="testMBI",
    other_state_code="NY",
    other_issuer="New York State Medicaid",
    organization_type=None,
):
    """
    Creates an Organization + OrganizationToName.
    """
    # authorized_official cannot be null → create a dummy individual
    ind = Individual.objects.create(
        id=uuid.uuid4(),
        gender="U",
        birth_date=datetime.date(1980, 1, 1),
    )

    IndividualToName.objects.create(
        individual=ind,
        first_name=authorized_official_first_name,
        last_name=authorized_official_last_name,
        name_use=_ensure_name_use(),
    )

    if id is None:
        id = uuid.uuid4()

    org = Organization.objects.create(
        id=id, authorized_official=ind, ein=legal_entity, parent_id=parent_id
    )

    if other_id_type or organization_type or npi_value:
        npi = Npi.objects.create(
            npi=npi_value or int(str(uuid.uuid4().int)[:10]),
            entity_type_code=1,
            enumeration_date=datetime.date(2000, 1, 1),
            last_update_date=datetime.date(2020, 1, 1),
        )

        clinical_organization = ClinicalOrganization.objects.create(organization=org, npi=npi)

        if other_id_type:
            OrganizationToOtherId.objects.create(
                npi=clinical_organization,
                other_id=other_id_name,
                other_id_type=other_id_type,
                state_code=other_state_code,
                issuer=other_issuer,
            )

        if organization_type:
            code = Nucc.objects.get(pk=organization_type)

            OrganizationToTaxonomy.objects.create(npi=clinical_organization, nucc_code=code)

    OrganizationToName.objects.create(
        organization=org,
        name=name,
        is_primary=True,
    )

    return org
