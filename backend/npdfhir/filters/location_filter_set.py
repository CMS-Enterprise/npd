import re
from django_filters import rest_framework as filters
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.db.models import F

from ..documentation_content import docs
from ..mappings import addressUseMapping
from ..models import Location
from .filter_utils import broad_address_match, field_based_vector_search


class LocationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="contains",
        help_text=docs.filters.location.name,
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type",
        help_text=docs.filters.organization.type,
    )

    address = filters.CharFilter(
        method="filter_address",
        help_text=docs.filters.address.full,
    )

    address_city = filters.CharFilter(
        method="filter_address_city",
        help_text=docs.filters.address.city,
    )

    address_state = filters.CharFilter(
        method="filter_address_state",
        help_text=docs.filters.address.state,
    )

    address_postalcode = filters.CharFilter(
        method="filter_address_postalcode",
        help_text=docs.filters.address.postalcode,
    )

    address_use = filters.ChoiceFilter(
        method="filter_address_use",
        choices=addressUseMapping.to_choices(),
        help_text=docs.filters.address.use,
    )

    near = filters.CharFilter(
        method="filter_distance",
        help_text=docs.filters.location.near,
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
        return field_based_vector_search(queryset, name, value, "organization__clinicalorganization__organizationtotaxonomy__nucc_code__code")

    def filter_address(self, queryset, name, value):
        location_filter_paths = [
            "address__address_us__delivery_line_1",
            "address__address_us__delivery_line_2",
            "address__address_us__city_name",
            "address__address_us__state_code__abbreviation",
            "address__address_us__zipcode"
        ]
        return broad_address_match(queryset, name, value, location_filter_paths)

    def filter_address_city(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "address__address_us__city_name")

    def filter_address_state(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "address__address_us__state_code__abbreviation")

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.filter(address__address_us__zipcode=value)

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
