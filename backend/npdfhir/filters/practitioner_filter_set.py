from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django_filters import rest_framework as filters

from ..mappings import addressUseMapping, genderMapping
from ..models import Provider
from ..utils import parse_identifier_query


class PractitionerFilterSet(filters.FilterSet):
    identifier = filters.CharFilter(
        method="filter_identifier",
        help_text="Filter by identifier (NPI or other). Format: value or system|value",
    )

    name = filters.CharFilter(
        method="filter_name", help_text="Filter by practitioner name (first, last, or full name)"
    )

    gender = filters.ChoiceFilter(
        method="filter_gender", choices=genderMapping.to_choices(), help_text="Filter by gender"
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type", help_text="Filter by practitioner type/taxonomy"
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

    def filter_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "individual__individualtoname__first_name",
                "individual__individualtoname__last_name",
                "individual__individualtoname__middle_name",
            )
        ).filter(search=value)

    def filter_practitioner_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("providertotaxonomy__nucc_code__display_name")
        ).filter(search=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "individual__individualtoaddress__address__address_us__delivery_line_1",
                "individual__individualtoaddress__address__address_us__delivery_line_2",
                "individual__individualtoaddress__address__address_us__city_name",
                "individual__individualtoaddress__address__address_us__state_code__abbreviation",
                "individual__individualtoaddress__address__address_us__zipcode",
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("individual__individualtoaddress__address__address_us__city_name")
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "individual__individualtoaddress__address__address_us__state_code__abbreviation"
            )
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("individual__individualtoaddress__address__address_us__zipcode")
        ).filter(search=value)

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(individual__individualtoaddress__address_use_id=value)
