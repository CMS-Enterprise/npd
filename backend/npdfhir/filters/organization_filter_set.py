from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django_filters import rest_framework as filters

from ..mappings import addressUseMapping
from ..models import Organization
from ..utils import parse_identifier_query


class OrganizationFilterSet(filters.FilterSet):
    name = filters.CharFilter(method="filter_name", help_text="Filter by organization name")

    identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI, EIN, or other). Format: value or system|value",
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type/taxonomy"
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

    class Meta:
        model = Organization
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
        return (
            queryset.annotate(search=SearchVector("organizationtoname__name"))
            .filter(search=value)
            .distinct()
        )

    def filter_identifier(self, queryset, name, value):
        from uuid import UUID

        system, identifier_id = parse_identifier_query(value)
        queries = Q(pk__isnull=True)

        if system:  # specific identifier search requested
            if system.upper() == "NPI":
                try:
                    queries = Q(clinicalorganization__npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass  # TODO: implement validationerror to show users that NPI must be an int
        else:  # general identifier search requested
            try:
                queries |= Q(clinicalorganization__npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            try:
                UUID(identifier_id)
                queries |= Q(ein__ein_id=identifier_id)
            except (ValueError, TypeError):
                pass

            queries |= Q(clinicalorganization__organizationtootherid__other_id=identifier_id)

        return queryset.filter(queries).distinct()

    def filter_organization_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "clinicalorganization__organizationtotaxonomy__nucc_code__display_name"
            )
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "organizationtoaddress__address__address_us__delivery_line_1",
                "organizationtoaddress__address__address_us__delivery_line_2",
                "organizationtoaddress__address__address_us__city_name",
                "organizationtoaddress__address__address_us__state_code__abbreviation",
                "organizationtoaddress__address__address_us__zipcode",
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("organizationtoaddress__address__address_us__city_name")
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "organizationtoaddress__address__address_us__state_code__abbreviation"
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("organizationtoaddress__address__address_us__zipcode")
        ).filter(search=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(organizationtoaddress__address_use_id=value)
