from datetime import date
import random
import uuid

from ...models import (
    Individual,
    IndividualToName,
    IndividualToAddress,
    Npi,
    Provider,
    ProviderToOtherId,
    ProviderToTaxonomy,
    FipsState,
)
from .utils import random_date
from .address import DefaultAddress
from typing import List


class DefaultName:
    def __init__(
        self,
        first_name: str = "Jane",
        middle_name: str = "C.",
        last_name: str = "Doe",
        name_use_id: int = 1,
    ):
        self.first_name = first_name
        self.middle_name = middle_name
        self.last_name = last_name
        self.name_use_id = name_use_id


class DefaultOtherID:
    def __init__(self, other_id: str = "123", other_id_type: int = 2, state: str = "DC"):
        self.other_id = other_id
        self.other_id_type = other_id_type
        self.state = state


class DefaultNPI:
    def __init__(
        self,
        npi: int = None,
        entity_type_code: int = 1,
        enumeration_date: date = None,
        last_update_date: date = None,
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
        self.create_if_not_exists()

    def create_if_not_exists(self):
        npi_obj = Npi.objects.filter(npi=self.npi)
        if npi_obj.exists():
            npi = npi_obj.first()
        else:
            npi = Npi.objects.create(
                npi=self.npi,
                entity_type_code=1,
                enumeration_date=self.enumeration_date,
                last_update_date=self.last_update_date,
            )
        self.npi = npi
        return self


class DefaultIndividual:
    def __init__(
        self,
        names: List[DefaultName] = None,
        addresses: List[DefaultAddress] = None,
        id: uuid = None,
        gender: str = "F",
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        if names is None:
            names = [DefaultName()]
        self.names = names
        self.gender = gender
        if addresses is None:
            addresses = [DefaultAddress()]
        self.addresses = addresses
        self.create_if_not_exists()

    def create_if_not_exists(self):
        individual = Individual.objects.filter(id=self.id)
        if individual.exists():
            self.individual = individual.first()
        else:
            self.individual = Individual.objects.create(
                id=self.id,
                gender=self.gender,
            )

            for name in self.names:
                IndividualToName.objects.create(
                    individual_id=self.id,
                    first_name=name.first_name,
                    last_name=name.last_name,
                    name_use_id=name.name_use_id,
                )
            for address in self.addresses:
                IndividualToAddress.objects.create(
                    individual_id=self.id,
                    address_id=address.id,
                    address_use_id=address.address_use_id,
                )
        return self.individual


class DefaultPractitioner:
    def __init__(
        self,
        individual: DefaultIndividual = None,
        taxonomies: List[str] = [],
        other_ids: List[DefaultOtherID] = [],
        npi: DefaultNPI = None,
    ):
        if individual is None:
            individual = DefaultIndividual()
        self.individual = individual
        self.taxonomies = taxonomies
        if npi is None:
            npi = DefaultNPI()
        self.npi = npi
        self.other_ids = other_ids
        self.create_if_not_exists()

    def create_if_not_exists(self):
        provider = Provider.objects.filter(individual_id=self.individual.id)
        if provider.exists():
            self.provider = provider.first()
        else:
            self.provider = Provider.objects.create(
                npi=self.npi.npi,
                individual_id=self.individual.id,
            )
            for taxonomy in self.taxonomies:
                ProviderToTaxonomy.objects.create(
                    npi=self.provider, nucc_code_id=taxonomy, id=uuid.uuid4()
                )

            for id in self.other_ids:
                state_code = FipsState.objects.filter(abbreviation=id.state).first()
                ProviderToOtherId.objects.create(
                    npi=self.provider,
                    other_id=id.other_id,
                    other_id_type_id=id.other_id_type,
                    state_code=state_code,
                )
        return self.provider
