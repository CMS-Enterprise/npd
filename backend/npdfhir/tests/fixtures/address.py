import random
import uuid

from django.contrib.gis.geos import Point

from ...models import Address, AddressUs, FipsState


class DefaultAddress:
    def __init__(
        self,
        id: uuid = None,
        line_1: str = "123 Main Street.",
        line_2: str = None,
        city: str = "Anytown",
        state: str = "DC",
        zip_code: str = "00000",
        x: float = 42.6680771,
        y: float = 73.8518804,
        address_use_id: int = 2,
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.line_1 = line_1
        self.line_2 = line_2
        self.city = city
        self.state = state
        self.zip_code = zip_code
        self.x = x
        self.y = y
        self.address_use_id = address_use_id
        self.create()

    def create(self):
        point = Point(self.x, self.y)
        self.address_us_id = random.randint(-100000000000, 100000000000)
        state_code = FipsState.objects.filter(abbreviation=self.state).first()
        self.address_us = AddressUs.objects.create(
            id=self.address_us_id,
            delivery_line_1=self.line_1,
            city_name=self.city,
            state_code=state_code,
            zipcode=self.zip_code,
            latitude=self.y,
            longitude=self.x,
            geolocation=point,
        )
        self.address = Address.objects.create(
            id=self.id,
            address_us=self.address_us,
        )
        return self
