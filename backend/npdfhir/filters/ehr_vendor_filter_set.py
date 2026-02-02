from django.contrib.postgres.search import SearchVector
from django_filters import rest_framework as filters

from ..models import EhrVendor
from ..utils import parse_identifier_query


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
        return queryset.annotate(search=SearchVector("name")).filter(search=value).distinct()

    def filter_identifier(self, queryset, name, value):
        from uuid import UUID

        system, identifier_id = parse_identifier_query(value)

        if system:  # specific identifier search requested
            if system.upper() == "NPI":
                # EHRVendors don't have NPI
                return queryset.none()

        try:
            UUID(identifier_id)
            # Support EIN identifier
            return queryset.filter(
                endpointinstance__locationtoendpointinstance__location__organization__ein__ein_id=identifier_id
            ).distinct()
        except (ValueError, TypeError):
            return queryset.none()
