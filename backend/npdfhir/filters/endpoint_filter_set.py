from django_filters import rest_framework as filters

from ..documentation_content import docs
from ..models import EndpointInstance


class EndpointFilterSet(filters.FilterSet):
    name = filters.CharFilter(
        field_name="name",
        lookup_expr="icontains",
        help_text=docs.filters.endpoint.name,
    )

    connection_type = filters.CharFilter(
        field_name="endpoint_connection_type__id",
        lookup_expr="icontains",
        help_text=docs.filters.endpoint.connection_type,
    )

    payload_type = filters.CharFilter(
        field_name="endpointinstancetopayload__payload_type__id",
        lookup_expr="icontains",
        help_text=docs.filters.endpoint.payload_type,
    )

    status = filters.CharFilter(
        method="filter_status",
        help_text=docs.filters.endpoint.status,
    )

    # We don't have a concept of endpoint organization at the moment
    # organization = filters.CharFilter(
    #    method="filter_organization", help_text="Filter by organization"
    # )

    class Meta:
        model = EndpointInstance
        fields = ["name", "connection_type", "payload_type", "status"]

    def filter_status(self, queryset, name, value):
        # needs to be implemented
        return queryset
