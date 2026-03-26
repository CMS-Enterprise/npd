from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..mappings import addressUseMapping
from ..models import Location
from .filter_utils import (
    broad_address_match,
    city_address_search,
    state_address_search,
    postalcode_address_search,
    address_use_search,
    general_filter_distance,
    gen_nucc_code_filter,
    filter_organization_name_gen,
    filter_identifier_general,
)


class LocationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="contains",
        help_text=docs.filters.location.name,
    )

    organization_name = filters.CharFilter(
        method="filter_organization_name",
        help_text=docs.filters.organization.name,
    )

    organization_identifier = filters.CharFilter(
        method="filter_organization_identifier",
        help_text=docs.filters.organization.identifier,
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
            "organization_name",
            "organization_identifier",
            "organization_type",
            "address",
            "address_city",
            "address_state",
            "address_postalcode",
            "address_use",
            "near",
        ]

    def filter_organization_name(self, queryset, name, value):
        return filter_organization_name_gen(queryset, name, value.upper(), prefix="organization__")

    def filter_organization_identifier(self, queryset, name, value):
        return filter_identifier_general(
            queryset,
            name,
            value,
            npi_prefix="organization__clinicalorganization__npi__",
            ein_prefix="ein__",
            other_prefix="organization__clinicalorganization__organizationtootherid__",
        )

    def filter_organization_type(self, queryset, name, value):
        return gen_nucc_code_filter(queryset, name, value)

    def filter_address(self, queryset, name, value):
        return broad_address_match(queryset, name, value)

    def filter_address_city(self, queryset, name, value):
        return city_address_search(queryset, name, value)

    def filter_address_state(self, queryset, name, value):
        return state_address_search(queryset, name, value)

    def filter_address_postalcode(self, queryset, name, value):
        return postalcode_address_search(queryset, name, value)

    def filter_address_use(self, queryset, name, value):
        return address_use_search(
            queryset, name, value, prefix="organization__organizationtoaddress"
        )

    def filter_distance(self, queryset, name, value):
        return general_filter_distance(queryset, name, value)
