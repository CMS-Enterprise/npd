from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..mappings import genderMapping
from ..models import ProviderToLocationView
from .filter_utils import (
    broad_address_match,
    city_address_search,
    state_address_search,
    postalcode_address_search,
    field_based_vector_search,
    filter_identifier_general,
    generic_filter_gender,
    filter_individual_name,
    general_filter_distance,
)


class PractitionerRoleFilterSet(filters.FilterSet):
    practitioner_table = "provider_to_organization"

    practitioner_name = filters.CharFilter(
        method="filter_practitioner_name",
        help_text=docs.filters.practitioner.name,
    )

    practitioner_gender = filters.ChoiceFilter(
        method="filter_practitioner_gender",
        choices=genderMapping.to_choices(),
        help_text=docs.filters.practitioner.gender,
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type",
        help_text=docs.filters.practitioner.type,
    )

    practitioner_identifier = filters.CharFilter(
        method="filter_practitioner_identifier",
        help_text=docs.filters.practitioner.identifier,
    )

    organization_name = filters.CharFilter(
        method="filter_organization_name",
        help_text=docs.filters.organization.name,
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type",
        help_text=docs.filters.organization.type,
    )

    location_near = filters.CharFilter(
        method="filter_distance",
        help_text=docs.filters.location.near,
    )

    location_address = filters.CharFilter(
        method="filter_address",
        help_text=docs.filters.address.full,
    )

    location_address_city = filters.CharFilter(
        method="filter_address_city",
        help_text=docs.filters.address.city,
    )

    location_address_state = filters.CharFilter(
        method="filter_address_state",
        help_text=docs.filters.address.state,
    )

    location_address_postalcode = filters.CharFilter(
        method="filter_address_postalcode",
        help_text=docs.filters.address.postalcode,
    )

    active = filters.BooleanFilter(
        field_name="active",
        help_text=docs.filters.practitioner_role.active,
    )

    role = filters.CharFilter(
        field_name="provider_role_code",
        lookup_expr="iexact",
        help_text=docs.filters.practitioner_role.role,
    )

    specialty = filters.CharFilter(
        method="filter_specialty",
        help_text=docs.filters.practitioner_role.specialty,
    )

    endpoint_connection_type = filters.CharFilter(
        method="filter_connection_type",
        help_text=docs.filters.endpoint.connection_type,
    )

    endpoint_payload_type = filters.CharFilter(
        method="filter_payload_type",
        help_text=docs.filters.endpoint.payload_type,
    )

    endpoint_status = filters.CharFilter(
        method="filter_endpoint_status",
        help_text=docs.filters.endpoint.status,
    )

    class Meta:
        model = ProviderToLocationView
        fields = [
            "practitioner_name",
            "practitioner_gender",
            "practitioner_type",
            "organization_name",
            "location_near",
            "organization_type",
            "active",
            "practitioner_identifier",
            "role",
            "specialty",
            "endpoint_connection_type",
            "endpoint_payload_type",
            "location_address",
            "location_address_city",
            "location_address_state",
            "location_address_postalcode",
        ]

    def filter_practitioner_name(self, queryset, name, value):
        return filter_individual_name(
            queryset,
            name,
            value,
            "provider_to_organization__individual",
        ).distinct()

    def filter_practitioner_gender(self, queryset, name, value):
        return generic_filter_gender(queryset, name, value, "provider_to_organization__individual")

    def filter_practitioner_type(self, queryset, name, value):
        return field_based_vector_search(
            queryset,
            name,
            value,
            "provider_to_organization__individual__providertotaxonomy__nucc_code__search_vector",
        )

    def filter_organization_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("provider_to_organization__organization__organizationtoname__name")
        ).filter(search=value)

    def filter_distance(self, queryset, name, value):
        return general_filter_distance(queryset, name, value, prefix="location__")

    def filter_organization_type(self, queryset, name, value):
        return queryset.filter(
            Q(
                provider_to_organization__organization__clinicalorganization__organizationtotaxonomy__nucc_code__display_name=value
            )
        ).distinct()

    def filter_practitioner_identifier(self, queryset, name, value):
        return filter_identifier_general(
            queryset,
            name,
            value,
            npi_path="provider_to_organization__individual__npi__npi",
            other_path="provider_to_organization__individual__providertootherid__other_id__icontains",
        )

    def filter_specialty(self, queryset, name, value):
        return queryset.filter(Q(specialty_id__iexact=value)).distinct()

    def filter_connection_type(self, queryset, name, value):
        return queryset.filter(
            location__locationtoendpointinstance__endpoint_instance__endpoint_connection_type_id=value
        )

    def filter_endpoint_status(self, queryset, name, value):
        return queryset.filter(
            location__locationtoendpointinstance__endpoint_instance__status=value
        )

    def filter_payload_type(self, queryset, name, value):
        return queryset.filter(
            location__locationtoendpointinstance__endpoint_instance__endpointinstancetopayload__payload_type_id=value
        ).distinct()

    def filter_endpoint_organization_id(self, queryset, name, value):
        # The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(location__organization__id=value)

    def filter_endpoint_organization_name(self, queryset, name, value):
        # The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(location__organization__organizationtoname__name=value)

    def filter_address(self, queryset, name, value):
        return broad_address_match(queryset, name, value, prefix="location__")

    def filter_address_city(self, queryset, name, value):
        return city_address_search(queryset, name, value, prefix="location__")

    def filter_address_state(self, queryset, name, value):
        return state_address_search(queryset, name, value, prefix="location__")

    def filter_address_postalcode(self, queryset, name, value):
        return postalcode_address_search(queryset, name, value, prefix="location__")
