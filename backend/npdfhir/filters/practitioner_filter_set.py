from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django_filters import rest_framework as filters

from ..mappings import addressUseMapping, genderMapping
from ..models import Provider
from ..utils import parse_identifier_query


class PractitionerFilterSet(filters.FilterSet):
    practitioner_table = None

    identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI or other). Format: value or system|value",
    )

    name = filters.CharFilter(
        method="filter_practitioner_name",
        help_text="Filter by practitioner name (first, middle, last, or full name). Name filter accepts websearch syntax.",
    )

    gender = filters.ChoiceFilter(
        method="filter_gender", choices=genderMapping.to_choices(), help_text="Filter by gender"
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type",
        help_text="Filter by practitioner type. Practitioner type filter accepts websearch syntax.",
    )

    address = filters.CharFilter(
        method="filter_address",
        help_text="Filter by any part of address. Address filter accepts websearch syntax.",
    )

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
        model = Provider
        fields = [
            "identifier",
            "name",
            "gender",
            "practitioner_type",
            "address",
            "address_city",
            "address_state",
            "address_postalcode",
            "address_use",
        ]

    def filter_gender(self, queryset, name, value):
        if value in genderMapping.keys():
            value = genderMapping.toNPD(value)

        return queryset.filter(individual__gender=value)

    def filter_identifier(self, queryset, name, value):
        system, identifier_id = parse_identifier_query(value)
        queries = Q(pk__isnull=True)

        if system:  # specific identifier search requested
            if system.upper() == "NPI":
                try:
                    queries = Q(npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass
        else:  # general identifier search requested
            try:
                queries |= Q(npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            queries |= Q(providertootherid__other_id=identifier_id)

        return queryset.filter(queries).distinct()

    def filter_practitioner_name(self, queryset, name, value):
        query = SearchQuery(f"{value.upper()}", search_type="websearch")
        return queryset.filter(individual__individualtoname__search_vector=query).distinct()

    def filter_practitioner_type(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch")
        return queryset.filter(providertotaxonomy__nucc_code__search_vector=query)

    def filter_address(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch")
        return queryset.filter(
            individual__individualtoaddress__address__address_us__search_vector=query
        )

    def filter_address_city(self, queryset, name, value):
        return queryset.filter(
            individual__individualtoaddress__address__address_us__city_name=value
        )

    def filter_address_state(self, queryset, name, value):
        return queryset.filter(
            individual__individualtoaddress__address__address_us__state_code__abbreviation=value
        )

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.filter(individual__individualtoaddress__address__address_us__zipcode=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(individual__individualtoaddress__address_use_id=value)
