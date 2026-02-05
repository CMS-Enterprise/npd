import json
import random

from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.db import IntegrityError
from faker import Faker

from npdfhir.tests.fixtures.endpoint import create_endpoint
from npdfhir.tests.fixtures.organization import create_organization
from npdfhir.tests.fixtures.practitioner import create_practitioner


class Command(BaseCommand):
    help = "Create test data for end-to-end specs"

    def generate_npi(self) -> int:
        return random.randint(1123456789, 2987654321)

    def to_json(self, **record) -> str:
        return json.dumps(record, cls=DjangoJSONEncoder, indent=2)

    def generate_sample_organizations(self, qty: int = 25):
        fake = Faker()
        for i in range(qty):
            name = f"TEST {fake.company()}"  # adding TEST here so that we can query results with the same name
            org = create_organization(
                name=name,
                # not bothering with checksum here
                npi_value=self.generate_npi(),
                authorized_official_first_name=fake.first_name(),
                authorized_official_last_name=fake.last_name(),
                other_state_code=fake.state_abbr(),
                other_issuer=fake.company(),
            )
            self.stdout.write(f"created Organization: {org.id} {name}")

    def generate_sample_practitioners(self, qty: int = 25):
        fake = Faker()
        for i in range(qty):
            first_name = f"TEST {fake.first_name()}"  # adding TEST here so that we can query results with the same name
            last_name = fake.last_name()
            practitioner = create_practitioner(
                first_name=first_name,
                last_name=last_name,
                npi_value=self.generate_npi(),
                gender=random.choice(["M", "F"]),
            )
            self.stdout.write(
                f"created Practitioner: {practitioner.individual.id} {first_name} {last_name}"
            )

    def handle(self, *args, **options):
        if options.get("seed", None):
            Faker.seed(int(options["seed"]))

        provider = create_practitioner()
        individualtoname = provider.individual.individualtoname_set.first()

        provider_report = self.to_json(
            individual__id=provider.individual.id,
            individual__individualtoname__first_name=individualtoname.first_name,
            individual__individualtoname__last_name=individualtoname.last_name,
            npi__npi=provider.npi.npi,
        )
        self.stdout.write(f"created Provider: {provider_report}")

        try:
            known_practitioner = create_practitioner(
                first_name="AAA",
                last_name="Test Practitioner",
                npi_value=1234567894,
            )
            individualtoname = known_practitioner.individual.individualtoname_set.first()
            self.stdout.write(
                f"created known Practitioner: {self.to_json(id=known_practitioner.individual.id, npi=known_practitioner.npi.npi, name=f'{individualtoname.first_name} {individualtoname.last_name}')}"
            )
        except IntegrityError:
            self.stdout.write("(practitioner with NPI 1234567894 already exists)")

        # Practitioner with the known NPI value as an "other_id" (not as NPI)
        # This tests that NPI-prefixed searches don't match other identifiers
        try:
            other_id_practitioner = create_practitioner(
                first_name="BBB",
                last_name="Other ID Practitioner",
                npi_value=self.generate_npi(),
                other_id="1234567894",
            )
            individualtoname = other_id_practitioner.individual.individualtoname_set.first()
            self.stdout.write(
                f"created other_id Practitioner: {self.to_json(id=other_id_practitioner.individual.id, npi=other_id_practitioner.npi.npi, other_id='1234567894', name=f'{individualtoname.first_name} {individualtoname.last_name}')}"
            )
        except IntegrityError:
            self.stdout.write("(practitioner with other_id 1234567894 already exists)")

        try:
            # one known NPI
            organization = create_organization(
                name="AAA Test Org", npi_value=1234567893, organization_type="261QP2000X"
            )
            organizationtoname = organization.organizationtoname_set.first()
            self.stdout.write(
                f"created Organization: {self.to_json(id=organization.id, organizationtoname__name=organizationtoname.name)}"
            )
        except IntegrityError:
            organization = None
            self.stdout.write("(organization with NPI 1234567893 already exists)")

        # Organization with the known NPI value as an "other_id" (not as NPI)
        # This tests that NPI-prefixed searches don't match other identifiers
        try:
            other_id_organization = create_organization(
                name="BBB Other ID Org",
                npi_value=self.generate_npi(),
                other_id_value="1234567893",
                organization_type="261QP2000X",
            )
            organizationtoname = other_id_organization.organizationtoname_set.first()
            self.stdout.write(
                f"created other_id Organization: {self.to_json(id=other_id_organization.id, other_id='1234567893', organizationtoname__name=organizationtoname.name)}"
            )
        except IntegrityError:
            self.stdout.write("(organization with other_id 1234567893 already exists)")

        if organization:
            endpoint = create_endpoint(organization=organization)
            self.stdout.write(f"created Endpoint: {self.to_json(id=endpoint.id)}")

        self.generate_sample_organizations(25)
        self.generate_sample_practitioners(25)
