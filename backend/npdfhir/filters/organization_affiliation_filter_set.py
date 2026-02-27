from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
from django_filters import rest_framework as filters

from ..utils import parse_identifier_query
from ..models import Nucc, Location


class OrganizationAffiliationFilterSet(filters.FilterSet):
    org_name = filters.CharFilter(method="filter_name", help_text="Filter by organization name")
    participating_org_name = filters.CharFilter(
        method="filter_participating_name", help_text="Filter by pariticipating organization name"
    )

    participating_organization_identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI, EIN, or other). Format: value or system|value",
    )

    participating_organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type/taxonomy"
    )

    address = filters.CharFilter(
        method="filter_location", help_text="Filter by any part of address"
    )

    address_city = filters.CharFilter(method="filter_address_city", help_text="Filter by city name")

    address_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by state (2-letter abbreviation)"
    )

    address_postalcode = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by postal code/zip code"
    )

    def filter_name(self, queryset, name, value):
        query = SearchQuery(f"{value}", search_type="phrase")
        return queryset.annotate(ehr_vendor_search=SearchVector("ehr_vendor_name")).filter(
            ehr_vendor_search=query
        )

    def filter_participating_name(self, queryset, name, value):
        return queryset.filter(organization_name__icontains=value)

    def filter_identifier(self, queryset, name, value):
        system, identifier_id = parse_identifier_query(value)
        queries = Q(pk__isnull=True)

        if system:
            if system.upper() == "NPI":
                try:
                    queries = Q(npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass
        else:
            try:
                queries |= Q(npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

        return queryset.filter(queries).distinct()

    def filter_organization_type(self, queryset, name, value):
        # Get codes corresponding to the display name
        codes = Nucc.objects.filter(display_name__icontains=value).values_list("code", flat=True)
        if not codes:
            return queryset.none()

        return queryset.filter(taxonomy_codes__overlap=list(codes))

    def filter_location(self, queryset, name, value):
        matching_location_ids = (
            Location.objects
            .annotate(
                location_search=SearchVector(
                    "name",
                    "address__address_us__delivery_line_1",
                    "address__address_us__delivery_line_2",
                    "address__address_us__city_name",
                    "address__address_us__state_code__abbreviation",
                    "address__address_us__zipcode",
                )
            )
            .filter(location_search=SearchQuery(value, search_type="websearch", config="english"))
            .values_list("id", flat=True)
        )

        # Filter affiliation rows where any location_id overlaps
        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_city(self, queryset, name, value):
        matching_location_ids = Location.objects.annotate(
            search=SearchVector("address__address_us__city_name")
        ).filter(
            search=value
        ).values_list("id", flat=True)

        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_state(self, queryset, name, value):
        matching_location_ids = Location.objects.annotate(
            search=SearchVector("address__address_us__state_code__abbreviation")
        ).filter(
            search=value
        ).values_list("id", flat=True)

        return queryset.filter(location_ids__overlap=list(matching_location_ids))

    def filter_address_postalcode(self, queryset, name, value):
        matching_location_ids = Location.objects.filter(
            address__address_us__zipcode=value
        ).values_list("id", flat=True)

        return queryset.filter(location_ids__overlap=list(matching_location_ids))
