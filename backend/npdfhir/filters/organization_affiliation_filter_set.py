from django.contrib.postgres.search import SearchVector, SearchQuery
from django.db.models import Q
from django_filters import rest_framework as filters

from ..mappings import addressUseMapping
from ..models import OrganizationView
from ..utils import parse_identifier_query


class OrganizationAffiliationFilterSet(filters.FilterSet):
    org_name = filters.CharFilter(method="filter_name", help_text="Filter by organization name")
    participating_org_name  = filters.CharFilter(method="filter_participating_name", help_text= "Filter by pariticipating organization name")

    participating_organization_identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI, EIN, or other). Format: value or system|value",
    )

    participating_organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type/taxonomy"
    )

    address = filters.CharFilter(method="filter_location", help_text="Filter by any part of address")

    address_city = filters.CharFilter(method="filter_address_city", help_text="Filter by city name")

    address_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by state (2-letter abbreviation)"
    )

    address_postalcode = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by postal code/zip code"
    )

    def filter_name(self, queryset, name, value):
        query = SearchQuery(f"{value}", search_type="phrase")
        return queryset.annotate(
            ehr_vendor_search=SearchVector("ehr_vendor_name")
        ).filter(
            ehr_vendor_search=query
        )

    def filter_participating_name(self, queryset, name, value):
        return queryset.filter(
            organization_name__icontains=value
        )

    def filter_identifier(self, queryset, name, value):
        from uuid import UUID

        system, identifier_id = parse_identifier_query(value)
        queries = Q(pk__isnull=True)

        if system:  # specific identifier search requested
            if system.upper() == "NPI":
                try:
                    queries = Q(organization__clinicalorganization__npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass  # TODO: implement validationerror to show users that NPI must be an int
        else:  # general identifier search requested
            try:
                queries |= Q(organization__clinicalorganization__npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            try:
                UUID(identifier_id)
                queries |= Q(ein__ein_id=identifier_id)
            except (ValueError, TypeError):
                pass

            queries |= Q(
                organization__clinicalorganization__organizationtootherid__other_id=identifier_id
            )

        return queryset.filter(queries).distinct()

    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "organization__clinicalorganization__organizationtotaxonomy__nucc_code__display_name"
            )
        ).filter(search=value)

    def filter_location(self, queryset, name, value):
        return queryset.annotate(
            location_search=SearchVector(
                "location_set__name",
                "location_set__address__address_us__delivery_line_1",
                "location_set__address__address_us__delivery_line_2",
                "location_set__address__address_us__city_name",
                "location_set__address__address_us__state_code__abbreviation",
                "location_set__address__address_us__zipcode",
            )
        ).filter(
            location_search=SearchQuery(value, search_type="websearch")
        ).distinct()

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "location_set__address__address_us__city_name"
            )
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "location_set__address__address_us__state_code__abbreviation"
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.filter(
            location_set__address__address_us__zipcode=value
        )
