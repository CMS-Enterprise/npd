from django.contrib.postgres.search import SearchQuery
from django.db.models import Q
from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..mappings import addressUseMapping, genderMapping
from ..models import ProviderView
from .filter_utils import filter_identifier_general


class PractitionerFilterSet(filters.FilterSet):
    practitioner_table = None

    identifier = filters.CharFilter(
        method="filter_identifier",
        help_text=docs.filters.practitioner.identifier,
    )

    name = filters.CharFilter(
        method="filter_practitioner_name",
        help_text=docs.filters.practitioner.name,
    )

    gender = filters.ChoiceFilter(
        method="filter_gender",
        choices=genderMapping.to_choices(),
        help_text=docs.filters.practitioner.gender,
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type",
        help_text=docs.filters.practitioner.type,
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
        model = ProviderView
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

        return queryset.filter(provider__individual__gender=value)

    def filter_identifier(self, queryset, name, value):
        return filter_identifier_general(queryset, name, value, npi_path="npi__npi", other_path="provider__providertootherid__other_id")

    def filter_practitioner_name(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch", config="english")
        return queryset.filter(
            provider__individual__individualtoname__search_vector=query
        ).distinct()

    def filter_practitioner_type(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch", config="english")
        return queryset.filter(provider__providertotaxonomy__nucc_code__search_vector=query)

    def filter_address(self, queryset, name, value):
        query = SearchQuery(value, search_type="websearch", config="english")
        return queryset.filter(
            provider__individual__individualtoaddress__address__address_us__search_vector=query
        )

    def filter_address_city(self, queryset, name, value):
        return queryset.filter(
            provider__individual__individualtoaddress__address__address_us__city_name=value
        )

    def filter_address_state(self, queryset, name, value):
        return queryset.filter(
            provider__individual__individualtoaddress__address__address_us__state_code__abbreviation=value
        )

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.filter(
            provider__individual__individualtoaddress__address__address_us__zipcode=value
        )

    def filter_address_use(self, queryset, name, value):
        if value in addressUseMapping.keys():
            value = addressUseMapping.toNPD(value)
        else:
            value = -1
        return queryset.filter(provider__individual__individualtoaddress__address_use_id=value)
