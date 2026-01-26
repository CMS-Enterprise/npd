import re
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.contrib.postgres.search import SearchVector
from django.db.models import Q
from django_filters import rest_framework as filters

from ..mappings import genderMapping
from ..models import ProviderToLocation
from ..utils import parse_identifier_query


class PractitionerRoleFilterSet(filters.FilterSet):
    practitioner_name = filters.CharFilter(
        method="filter_practitioner_name",
        help_text="Filter by practitioner name (first, last, or full name)",
    )

    practitioner_gender = filters.ChoiceFilter(
        method="filter_practitioner_gender",
        choices=genderMapping.to_choices(),
        help_text="Filter by practitioner gender",
    )

    practitioner_type = filters.CharFilter(
        method="filter_practitioner_type", help_text="Filter by practitioner type/taxonomy"
    )

    organization_name = filters.CharFilter(
        method="filter_organization_name", help_text="Filter by organization name"
    )

    location_near = filters.CharFilter(
        method="filter_distance",
        help_text="Filter location by distance from a point expressed as [latitude]|[longitude]|[distance]|[units]. If no units are provided, km is assumed.",
    )

    organization_type = filters.CharFilter(
        method="filter_organization_type", help_text="Filter by organization type"
    )

    active = filters.BooleanFilter(field_name="active", help_text="Filter by active status")

    practitioner_identifier = filters.CharFilter(
        method="filter_practitioner_identifier", help_text="Filter by practitioner identifier"
    )

    role = filters.CharFilter(
        field_name="provider_role_code",
        lookup_expr="iexact",
        help_text="Filter by provider role code",
    )

    specialty = filters.CharFilter(
        method="filter_specialty", help_text="Filter by Nucc/Snomed specialty code"
    )

    endpoint_connection_type = filters.CharFilter(
        method="filter_connection_type", help_text="Filter providers by endpoint connection type"
    )

    endpoint_payload_type = filters.CharFilter(
        method="filter_payload_type", help_text="Filter providers by endpoint payload type"
    )

    endpoint_status = filters.CharFilter(
        method="filter_endpoint_status", help_text="Filter providers by endpoint status"
    )

    endpoint_organization_id = filters.UUIDFilter(
        method="filter_endpoint_organization_id",
        help_text="Filter by the UUID of the organization associated with endpoints",
    )

    endpoint_organization_name = filters.CharFilter(
        method="filter_endpoint_organization_name",
        help_text="Filter by the name of the organization associated with endpoints",
    )

    location_address = filters.CharFilter(
        method="filter_address", help_text="Filter by the location address"
    )

    location_city = filters.CharFilter(
        method="filter_address_city", help_text="Filter by the location city"
    )

    location_state = filters.CharFilter(
        method="filter_address_state", help_text="Filter by the location state"
    )

    location_zip_code = filters.CharFilter(
        method="filter_address_postalcode", help_text="Filter by the location postal code"
    )

    class Meta:
        model = ProviderToLocation
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
            "endpoint_organization_id",
            "endpoint_organization_name",
            "location_address",
            "location_city",
            "location_state",
            "location_zip_code",
        ]

    def filter_practitioner_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "provider_to_organization__individual__individual__individualtoname__first_name",
                "provider_to_organization__individual__individual__individualtoname__last_name",
                "provider_to_organization__individual__individual__individualtoname__middle_name",
            )
        ).filter(search=value)

    def filter_practitioner_gender(self, queryset, name, value):
        if value in genderMapping.keys():
            gender = genderMapping.toNPD(value)
            return queryset.filter(provider_to_organization__individual__individual__gender=gender)
        return queryset

    def filter_practitioner_type(self, queryset, name, value):
        return queryset.filter(
            provider_to_organization__individual__providertotaxonomy__nucc_code__code=value
        ).distinct()

    def filter_organization_name(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("provider_to_organization__organization__organizationtoname__name")
        ).filter(search=value)

    def filter_distance(self, queryset, name, value):
        pattern = r"(-?\d+\.?\d*)\|(-?\d+\.?\d*)\|(\d+\.?\d*)\|?(km|mi|ft)?"
        match = re.fullmatch(pattern, value)
        if match:
            lat, lon, distance, units = match.groups()
            lon = float(lon)
            lat = float(lat)
            distance = float(distance)
            user_location = Point(lon, lat, srid=4326)
            match units:
                case "mi":
                    distance_function = D(mi=distance)
                case "ft":
                    distance_function = D(ft=distance)
                case _:
                    distance_function = D(km=distance)
            return queryset.filter(
                location__address__address_us__geolocation__distance_lte=(
                    user_location,
                    distance_function,
                )
            )
        else:
            return ProviderToLocation.objects.none()

    def filter_organization_type(self, queryset, name, value):
        return queryset.filter(
            Q(
                provider_to_organization__organization__clinicalorganization__organizationtotaxonomy__nucc_code__code=value
            )
        ).distinct()

    def filter_practitioner_identifier(self, queryset, name, value):
        system, identifier_id = parse_identifier_query(value)
        queries = Q(pk__isnull=True)

        if system:  # specific identifier search requested
            if system.upper() == "NPI":
                try:
                    queries = Q(provider_to_organization__individual__npi__npi=int(identifier_id))
                except (ValueError, TypeError):
                    pass
        else:  # general identifier search requested
            try:
                queries |= Q(provider_to_organization__individual__npi__npi=int(identifier_id))
            except (ValueError, TypeError):
                pass

            queries |= Q(
                provider_to_organization__individual__providertootherid__other_id__icontains=identifier_id
            )

        return queryset.filter(queries).distinct()

    def filter_specialty(self, queryset, name, value):
        return queryset.filter(Q(specialty_id__iexact=value)).distinct()

    def filter_connection_type(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("other_endpoint__endpoint_instance__endpoint_connection_type__id")
        ).filter(search=value)

    def filter_endpoint_status(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("location__locationtoendpointinstance__endpoint_instance__status")
        ).filter(search=value)

    def filter_payload_type(self, queryset, name, value):
        return queryset.filter(
            location__locationtoendpointinstance__endpoint_instance__endpointinstancetopayload__payload_type__id=value
        ).distinct()

    def filter_endpoint_organization_id(self, queryset, name, value):
        # The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(location__organization__id=value)

    def filter_endpoint_organization_name(self, queryset, name, value):
        # The parent of the organization that owns the location the endpoint is attached to
        return queryset.filter(location__organization__organizationtoname__name=value)

    def filter_address(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector(
                "location__address__address_us__delivery_line_1",
                "location__address__address_us__delivery_line_2",
                "location__address__address_us__city_name",
                "location__address__address_us__state_code__abbreviation",
                "location__address__address_us__zipcode",
            )
        ).filter(search=value)

    def filter_address_city(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("location__address__address_us__city_name")
        ).filter(search=value)

    def filter_address_state(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("location__address__address_us__state_code__abbreviation")
        ).filter(search=value)

    def filter_address_postalcode(self, queryset, name, value):
        return queryset.annotate(
            search=SearchVector("location__address__address_us__zipcode")
        ).filter(search=value)
