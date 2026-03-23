from django_filters import rest_framework as filters

from ..models import EhrVendor
from .filter_utils import filter_identifier_general, field_based_vector_search


class EhrVendorFilterSet(filters.FilterSet):
    name = filters.CharFilter(method="filter_name", help_text="Filter by organization name")

    identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI, EIN, or other). Format: value or system|value",
    )

    class Meta:
        model = EhrVendor
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
        return field_based_vector_search(queryset, name, value, "name").distinct()

    def filter_identifier(self, queryset, name, value):
        return filter_identifier_general(
            queryset,
            name,
            value,
            ein_prefix="endpointinstance__locationtoendpointinstance__location__organization__ein__",
        )
