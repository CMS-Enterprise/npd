from django_filters import rest_framework as filters

from ..models import Nucc, Location
from .filter_utils import (
    filter_identifier_general,
    broad_address_match,
    field_based_vector_search,
    city_address_search,
    state_address_search,
    postalcode_address_search,
)


class OrganizationAffiliationFilterSet(filters.FilterSet):
    primary_organization_name = filters.CharFilter(
        method="filter_name", help_text="Filter by organization name"
    )
    participating_organization_name = filters.CharFilter(
        method="filter_participating_name", help_text="Filter by pariticipating organization name"
    )

    participating_organization_identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI, EIN, or other). Format: value or system|value",
    )

    participating_organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type/taxonomy"
    )

    location_address = filters.CharFilter(
        method="filter_location", help_text="Filter by any part of address"
    )

    location_address_city = filters.CharFilter(
        method="filter_address_city", help_text="Filter by city name"
    )

    location_address_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by state (2-letter abbreviation)"
    )

    location_address_postalcode = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by postal code/zip code"
    )

    def filter_name(self, queryset, name, value):
        return field_based_vector_search(queryset, name, value, "ehr_vendor_name")

    def filter_participating_name(self, queryset, name, value):
        return queryset.filter(organization_name__icontains=value)

    # Filter generally by clinical organizational
    def filter_identifier(self, queryset, name, value):
        return filter_identifier_general(queryset, name, value, npi_prefix="")

    def filter_organization_type(self, queryset, name, value):
        # Get codes corresponding to the display name
        codes = Nucc.objects.filter(display_name__icontains=value).values_list("code", flat=True)
        if not codes:
            return queryset.none()

        return queryset.filter(taxonomy_codes__overlap=list(codes))

    def filter_location(self, queryset, name, value):
        matching_location_ids = broad_address_match(Location.objects, name, value).values_list(
            "id", flat=True
        )

        # Filter affiliation rows where any location_id overlaps
        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_city(self, queryset, name, value):
        matching_location_ids = city_address_search(Location.objects, name, value).values_list(
            "id", flat=True
        )

        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_state(self, queryset, name, value):
        matching_location_ids = state_address_search(Location.objects, name, value).values_list(
            "id", flat=True
        )

        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_postalcode(self, queryset, name, value):
        matching_location_ids = postalcode_address_search(
            Location.objects, name, value
        ).values_list("id", flat=True)

        return queryset.filter(location_ids__overlap=list(matching_location_ids))
