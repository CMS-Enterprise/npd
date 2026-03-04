import json
import random

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from faker import Faker


from npdfhir.tests.fixtures.organization import DefaultOrganization
from npdfhir.tests.fixtures.practitioner import (
    DefaultPractitioner,
    DefaultIndividual,
    DefaultOtherID,
    DefaultNPI,
    DefaultName,
)

from npdfhir.models import OrganizationView, ProviderView


class Command(BaseCommand):
    help = "Create test data for end-to-end specs"

    def to_json(self, **record) -> str:
        return json.dumps(record, cls=DjangoJSONEncoder, indent=2)

    def generate_sample_organizations(self, qty: int = 25):
        fake = Faker()
        for i in range(qty):
            name = f"TEST {fake.company()}"  # adding TEST here so that we can query results with the same name
            org = DefaultOrganization(
                names=[name],
                authorized_official=DefaultIndividual(
                    names=[DefaultName(first_name=fake.first_name(), last_name=fake.last_name())]
                ),
            )
            self.stdout.write(f"created Organization: {org.id} {name}")

    def generate_sample_practitioners(self, qty: int = 25):
        fake = Faker()
        for i in range(qty):
            name = {
                "first_name": f"TEST {fake.first_name()}",  # adding TEST here so that we can query results with the same name
                "last_name": fake.last_name(),
            }
            practitioner = DefaultPractitioner(
                individual=DefaultIndividual(
                    names=[DefaultName(**name)], gender=random.choice(["M", "F"])
                ),
            )
            self.stdout.write(
                f"created Practitioner: {practitioner.individual.id} {' '.join(name.values())}"
            )

    def handle(self, *args, **options):
        if options.get("seed", None):
            Faker.seed(int(options["seed"]))

        provider = DefaultPractitioner(taxonomies=["207R00000X"])

        self.stdout.write(f"created Practitioner: {provider.individual.id}")

        try:
            name = {"first_name": "AAA", "last_name": "Test Practitioner"}
            known_practitioner = DefaultPractitioner(
                individual=DefaultIndividual(names=[DefaultName(**name)]),
                npi=DefaultNPI(npi=1234567894),
                taxonomies=["207R00000X"],
            )
            self.stdout.write(
                f"created known Practitioner: {self.to_json(id=known_practitioner.individual.id, npi=known_practitioner.npi.npi.npi, name=' '.join(name.values()))}"
            )
        except IntegrityError:
            self.stdout.write("(practitioner with NPI 1234567894 already exists)")

        # Practitioner with the known NPI value as an "other_id" (not as NPI)
        # This tests that NPI-prefixed searches don't match other identifiers
        try:
            name = {"first_name": "BBB", "last_name": "Other ID Practitioner"}
            other_id = "1234567894"
            other_id_practitioner = DefaultPractitioner(
                individual=DefaultIndividual(names=[DefaultName(**name)]),
                other_ids=[DefaultOtherID(other_id=other_id)],
            )
            self.stdout.write(
                f"created other_id Practitioner: {self.to_json(id=other_id_practitioner.individual.id, npi=other_id_practitioner.npi.npi.npi, other_id=other_id, name=' '.join(name.values()))}"
            )
        except IntegrityError:
            self.stdout.write("(practitioner with other_id 1234567894 already exists)")

        try:
            # one known NPI
            name = "AAA Test Org"
            organization = DefaultOrganization(
                names=[name], npi=DefaultNPI(npi=1234567893), taxonomies=["261QP2000X"]
            )
            self.stdout.write(
                f"created Organization: {self.to_json(id=organization.id, organizationtoname__name=name)}"
            )
        except IntegrityError:
            organization = None
            self.stdout.write("(organization with NPI 1234567893 already exists)")

        # Organization with the known NPI value as an "other_id" (not as NPI)
        # This tests that NPI-prefixed searches don't match other identifiers
        try:
            name = "BBB Other ID Org"
            other_id = "1234567893"
            other_id_organization = DefaultOrganization(
                names=[name],
                other_ids=[DefaultOtherID(other_id=other_id)],
                taxonomies=["261QP2000X"],
            )
            self.stdout.write(
                f"created other_id Organization: {self.to_json(id=other_id_organization.id, other_id=other_id, organizationtoname__name=name)}"
            )
        except IntegrityError:
            self.stdout.write("(organization with other_id 1234567893 already exists)")

        self.generate_sample_organizations(25)
        OrganizationView.refresh_materialized_view()
        self.generate_sample_practitioners(25)
        ProviderView.refresh_materialized_view()
