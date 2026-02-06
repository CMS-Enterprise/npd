import random
import uuid

from django.contrib.gis.geos import Point

from ...models import Address, AddressUs, FipsState, Location, FhirAddressUse, OrganizationToAddress
from .organization import create_organization


def create_address(
    city="Albany",
    state="NY",
    zipcode="12207",
    addr_line_1="123 Main St",
    x=42.6680771,
    y=-73.8518804,
):
    fips_code = FipsState.objects.get(abbreviation=state)

    point = Point(x, y)

    addr_us = AddressUs.objects.create(
        id=random.randint(-100000000000, 100000000000),
        delivery_line_1=addr_line_1,
        city_name=city,
        state_code_id=fips_code.id,
        zipcode=zipcode,
        latitude=y,
        longitude=x,
        geolocation=point,
    )

    address = Address.objects.create(
        id=uuid.uuid4(),
        address_us=addr_us,
    )

    return address


def create_location(
    id=None,
    organization=None,
    organization_name="Test Organization",
    name="Test Location",
    city="Albany",
    state="NY",
    zipcode="12207",
    addr_line_1="123 Main St",
    x=42.6680771,
    y=-73.8518804,
    address_use="work",
):
    """
    Creates AddressUs → Address → Location.
    """
    if organization is None:
        organization = create_organization(name=organization_name)
    address = create_address(
        city=city, state=state, zipcode=zipcode, addr_line_1=addr_line_1, x=x, y=y
    )

    use = FhirAddressUse.objects.get(value=address_use)

    OrganizationToAddress.objects.create(
        organization=organization, address=address, address_use=use
    )

    if id is None:
        id = uuid.uuid4()

    loc = Location.objects.create(
        id=id,
        name=name,
        organization=organization,
        address=address,
        active=True,
    )

    return loc
