import re
from django.contrib.postgres.search import SearchVector
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import F

from ..mappings import addressUseMapping
from ..models import Location


class LocationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="contains", help_text="Filter by location name"
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type"
    )

    address = filters.CharFilter(method="filter_address", help_text="Filter by any part of address")

    address_city = filters.CharFilter(method="filter_address_city", help_text="Filter by city name")

    address_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by state (2-letter abbreviation)"
    )

    address_postalcode = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by postal code/zip code"
    )

    address_use = filters.ChoiceFilter(
        method="filter_address_use",
        choices=addressUseMapping.to_choices(),
        help_text="Filter by address use type",
    )

    near = filters.CharFilter(
        method="filter_distance",
        help_text="Filter by distance from a point expressed as [latitude]|[longitude]|[distance]|[units]. If no units are provided, km is assumed.",
    )

    class Meta:
        model = Location
        fields = [
            "name",
            "address",
            "address_city",
            "address_state",
            "address_postalcode",
            "address_use",
            "near",
        ]

    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "organization__clinicalorganization__organizationtotaxonomy__nucc_code__code"
            )
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "address__address_us__delivery_line_1",
                "address__address_us__delivery_line_2",
                "address__address_us__city_name",
                "address__address_us__state_code__abbreviation",
                "address__address_us__zipcode",
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("address__address_us__city_name")).filter(
            search=value
        )

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("address__address_us__state_code__abbreviation")
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(search=SearchVector("address__address_us__zipcode")).filter(
            search=value
        )

    def filter_address_use(self, queryset, name, value):
        return queryset.filter(
            organization__organizationtoaddress__address=F("address"),
            organization__organizationtoaddress__address_use__value=value,
        ).distinct()

    def filter_distance(self, queryset, name, value):
        pattern = r"(-?\d+\.?\d*)\|(-?\d+\.?\d*)\|(\d+\.?\d*)\|?(km|mi|ft)?"
        match = re.fullmatch(pattern, value)
        if match:
            lat, lon, distance, units = match.groups()
            lon = float(lon)
            lat = float(lat)
            distance = float(distance)
            user_location = Point(lon, lat, srid=4326)
            match units:
                case "mi":
                    distance_function = D(mi=distance)
                case "ft":
                    distance_function = D(ft=distance)
                case _:
                    distance_function = D(km=distance)
            return queryset.filter(
                address__address_us__geolocation__distance_lte=(user_location, distance_function)
            )
        else:
            return Location.objects.none()
