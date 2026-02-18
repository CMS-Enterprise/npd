from datetime import date
import random
import uuid

from ...models import (
    Individual,
    IndividualToName,
    Npi,
    Provider,
    ProviderToOtherId,
    ProviderToTaxonomy,
)
from .utils import random_date
from typing import TypedDict, List


class DefaultName(TypedDict):
    first_name: str = "Jane"
    middle_name: str = "C."
    last_name: str = "Doe"
    name_use_id: int = 1


class DefaultOtherIDs(TypedDict):
    other_id: str = "123"
    other_id_type: int = 2
    state: str = "DC"


class DefaultNPI:
    def __init__(
        self, npi: int, entity_type_code: int, enumeration_date: date, last_update_date: date
    ):
        if npi is None:
            self.npi = random.randint(1000000000, 9999999999)
        else:
            self.npi = npi

        self.entity_type_code = entity_type_code

        if enumeration_date is None:
            self.enumeration_date = random_date()
        else:
            self.enumeration_date = enumeration_date

        if last_update_date is None:
            self.last_update_date = random_date(start_date=enumeration_date)
        else:
            self.last_update_date = last_update_date

    def create_if_not_exists(self):
        npi = Npi.filter(npi=self.npi)
        if not npi.exists():
            Npi.objects.create(
                npi=self.npi,
                entity_type_code=1,
                enumeration_date=self.enumeration_date,
                last_update_date=self.last_update_date,
            )
        return self


class DefaultIndividual:
    def __init__(
        self,
        names: List[DefaultName],
        id: uuid = None,
        gender: str = "F",
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.names = names
        self.gender = gender

    def create_if_not_exists(self):
        individual = Individual.objects.filter(id=self.id)
        if individual.exists():
            self.individual = individual
        else:
            self.individual = Individual.objects.create(
                id=self.id,
                gender=self.gender,
            )

            for name in self.names:
                IndividualToName.objects.create(
                    individual=self.individual,
                    first_name=name.first_name,
                    last_name=name.last_name,
                    name_us_id=name.name_use_id,
                )
        return self.individual


class DefaultPractitioner:
    def __init__(
        self,
        individual: DefaultIndividual,
        taxonomies: List[str],
        other_ids: List[DefaultOtherIDs],
        npi: DefaultNPI,
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id

        self.individual = individual.create_if_not_exists()
        self.taxonomies = taxonomies
        self.npi = npi.create_if_not_exists()

    def create_if_not_exists(self):
        provider = Provider.filter(id=self.id)
        if provider.exists():
            self.provider = provider
        else:
            self.provider = Provider.objects.create(
                npi=self.npi,
                individual=self.individual,
            )
            for taxonomy in self.taxonomies:
                ProviderToTaxonomy.objects.create(npi=provider, nucc_code=taxonomy, id=uuid.uuid4())

            for id in self.other_ids:
                ProviderToOtherId.objects.create(
                    npi=provider,
                    other_id=id.other_id,
                    other_id_type_code=self.other_id_type_code,
                    state_code__abbreviation=id.state,
                )
        return self.provider
