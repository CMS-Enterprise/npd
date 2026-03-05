from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..mappings import addressUseMapping
from ..models import OrganizationView
from .filter_utils import broad_address_match, field_based_vector_search, filter_identifier_general


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
        query = SearchQuery(f"{value.upper()}", search_type="websearch", config="english")
        return queryset.filter(organization__organizationtoname__search_vector=query)

    def filter_identifier(self, queryset, name, value):
        return filter_identifier_general(queryset, name, value, npi_path="organization__clinicalorganization__npi__npi", ein_path="ein__ein_id", other_path="organization__clinicalorganization__organizationtootherid__other_id")

    def filter_organization_type(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "organization__clinicalorganization__organizationtotaxonomy__nucc_code__display_name")

    def filter_address(self, queryset, name, value):
        location_address_paths = [
            "organization__organizationtoaddress__address__address_us__delivery_line_1",
            "organization__organizationtoaddress__address__address_us__delivery_line_2",
            "organization__organizationtoaddress__address__address_us__city_name",
            "organization__organizationtoaddress__address__address_us__state_code__abbreviation",
            "organization__organizationtoaddress__address__address_us__zipcode"
        ]
        return broad_address_match(queryset, name, value, location_address_paths)

    def filter_address_city(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "organization__organizationtoaddress__address__address_us__city_name")

    def filter_address_state(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "organization__organizationtoaddress__address__address_us__state_code__abbreviation")

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.filter(
            organization__organizationtoaddress__address__address_us__zipcode=value
        )

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(organization__organizationtoaddress__address_use_id=value)
