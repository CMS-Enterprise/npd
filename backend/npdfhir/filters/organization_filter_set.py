from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..mappings import addressUseMapping
from ..models import OrganizationView
from .filter_utils import (
    broad_address_match,
    field_based_vector_search,
    filter_identifier_general,
    address_use_search,
    city_address_search,
    state_address_search,
    postalcode_address_search,
)


class OrganizationFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        method="filter_name",
        help_text=docs.filters.organization.name,
    )

    identifier = filters.CharFilter(
        method="filter_identifier",
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

    class Meta:
        model = OrganizationView
        fields = [
            "name",
            "identifier",
            "organization_type",
            "address",
            "address_city",
            "address_state",
            "address_postalcode",
            "address_use",
        ]

    def filter_name(self, queryset, name, value):
        return field_based_vector_search(
            queryset, name, value.upper(), "organization__organizationtoname__search_vector"
        )

    def filter_identifier(self, queryset, name, value):
        return filter_identifier_general(
            queryset,
            name,
            value,
            npi_prefix="organization__clinicalorganization__npi__",
            ein_prefix="ein__",
            other_prefix="organization__clinicalorganization__organizationtootherid__",
        )

    def filter_organization_type(self, queryset, name, value):
        return field_based_vector_search(
            queryset,
            name,
            value,
            "organization__clinicalorganization__organizationtotaxonomy__nucc_code__display_name",
        )

    def filter_address(self, queryset, name, value):
        return broad_address_match(
            queryset, name, value, prefix="organization__organizationtoaddress__"
        )

    def filter_address_city(self, queryset, name, value):
        return city_address_search(queryset, name, value, prefix="organization__organizationtoaddress__")

    def filter_address_state(self, queryset, name, value):
        return state_address_search(queryset, name, value, prefix="organization__organizationtoaddress__")

    def filter_address_postalcode(self, queryset, name, value):
        return postalcode_address_search(queryset, name, value, prefix="organization__organizationtoaddress__")

    def filter_address_use(self, queryset, name, value):
        return address_use_search(queryset, name, value, prefix="organization__organizationtoaddress")
