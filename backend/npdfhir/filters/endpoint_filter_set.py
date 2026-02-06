from django_filters import rest_framework as filters

from ..models import EndpointInstance


class EndpointFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name", lookup_expr="icontains", help_text="Filter by name"
    )

    connection_type = filters.CharFilter(
        field_name="endpoint_connection_type__id",
        lookup_expr="icontains",
        help_text="Filter by connection type",
    )

    payload_type = filters.CharFilter(
        field_name="endpointinstancetopayload__payload_type__id",
        lookup_expr="icontains",
        help_text="Filter by payload type",
    )

    status = filters.CharFilter(method="filter_status", help_text="Filter by status")

    organization = filters.CharFilter(
        method="filter_organization", help_text="Filter by organization"
    )

    class Meta:
        model = EndpointInstance
        fields = ["name", "connection_type", "payload_type", "status", "organization"]

    def filter_status(self, queryset, name, value):
        # needs to be implemented
        return queryset

    def filter_organization(self, queryset, name, value):
        # needs to be implemented
        return queryset
