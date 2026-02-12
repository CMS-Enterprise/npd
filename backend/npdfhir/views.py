from uuid import UUID

from django.conf import settings
from django.db.models import CharField, Exists, F, OuterRef, Subquery, Value, Prefetch
from django.db.models.functions import Concat
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.html import escape
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.renderers import BrowsableAPIRenderer
from rest_framework.response import Response
from rest_framework.filters import OrderingFilter

from .documentation_content import docs
from .pagination import CustomPaginator
from .renderers import FHIRRenderer

from .filters.endpoint_filter_set import EndpointFilterSet
from .filters.location_filter_set import LocationFilterSet
from .filters.organization_filter_set import OrganizationFilterSet
from .filters.practitioner_filter_set import PractitionerFilterSet
from .filters.practitioner_role_filter_set import PractitionerRoleFilterSet

from .models import (
    EndpointInstance,
    Location,
    LocationToEndpointInstance,
    Organization,
    ProviderView,
    ProviderToLocationView,
    OrganizationToAddress,
    OrganizationView,
    IndividualToAddress,
)

from .serializers import (
    BundleSerializer,
    EndpointSerializer,
    LocationSerializer,
    OrganizationAffiliationSerializer,
    OrganizationSerializer,
    PractitionerRoleSerializer,
    PractitionerSerializer,
    CapabilityStatementSerializer,
)

DEBUG = settings.DEBUG


def index(request):
    return HttpResponse("Connection to npd database: successful")


def health(request):
    return HttpResponse("healthy")


class ParamOrderingFilter(OrderingFilter):
    ordering_param = "_sort"


class FHIREndpointViewSet(viewsets.GenericViewSet):
    queryset = (
        EndpointInstance.objects.all()
        .prefetch_related(
            "endpoint_connection_type",
            "environment_type",
            "endpointinstancetopayload_set",
            "endpointinstancetopayload_set__payload_type",
            "endpointinstancetopayload_set__mime_type",
            "endpointinstancetootherid_set",
        )
        .annotate(ehr_vendor_name=F("ehr_vendor__name"))
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = EndpointFilterSet
    ordering = ["name"]
    ordering_fields = ["name", "address", "ehr_vendor_name"]
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.endpoint.list_response)}
    )
    def list(self, request):
        endpoints = self.filter_queryset(self.queryset)
        paginated_endpoints = self.paginate_queryset(endpoints)

        serialized_endpoints = EndpointSerializer(
            paginated_endpoints, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_endpoints, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.endpoint.retrieve_response)}
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Endpoint {escape(id)} not found", status=404)

        endpoint = get_object_or_404(
            self.queryset,
            id=id,
        )

        serialized_endpoint = EndpointSerializer(endpoint, context={"request": request})

        response = Response(serialized_endpoint.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.endpoint.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.endpoint.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.endpoint.default_sort}"
    )  # list description
    retrieve.__doc__ = docs.endpoints.endpoint.retrieve_description  # retrieve description


class FHIRPractitionerViewSet(viewsets.GenericViewSet):
    queryset = ProviderView.objects.all().prefetch_related(
        "provider__individual",
        "provider__npi",
        "provider",
        Prefetch(
            "provider__individual__individualtoaddress_set",
            queryset=IndividualToAddress.objects.select_related(
                "address_use", "address__address_us", "address__address_us__state_code"
            ),
        ),
        "provider__individual__individualtophone_set",
        "provider__individual__individualtoemail_set",
        "provider__individual__individualtoname_set",
        "provider__providertootherid_set",
        "provider__providertotaxonomy_set",
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = PractitionerFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"

    ordering = [
        "last_name",
        "first_name",
    ]

    ordering_fields = [
        "last_name",
        "first_name",
        "npi_value",
    ]

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.practitioner.list_response)}
    )
    def list(self, request):
        providers = self.filter_queryset(self.queryset)
        paginated_providers = self.paginate_queryset(providers)

        serialized_providers = PractitionerSerializer(paginated_providers, many=True)
        bundle = BundleSerializer(serialized_providers, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.practitioner.retrieve_response)}
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Practitioner {escape(id)} not found", status=404)

        provider = get_object_or_404(
            self.queryset,
            provider_id=id,
        )

        serialized_practitioner = PractitionerSerializer(provider)

        response = Response(serialized_practitioner.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.practitioner.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.practitioner.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.practitioner.default_sort}"
    )  # list description
    retrieve.__doc__ = docs.endpoints.practitioner.retrieve_description  # retrieve description


class FHIRPractitionerRoleViewSet(viewsets.GenericViewSet):
    queryset = (
        ProviderToLocationView.objects.all()
        .select_related("location")
        .prefetch_related("provider_to_organization", "location__locationtoendpointinstance_set")
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = PractitionerRoleFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"

    ordering = ["location_name"]
    ordering_fields = [
        "location_name",
        "practitioner_first_name",
        "practitioner_last_name",
        "organization_name",
    ]

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.practitioner_role.list_response)}
    )
    def list(self, request):
        practitionerroles = self.filter_queryset(self.queryset)
        paginated_practitionerroles = self.paginate_queryset(practitionerroles)

        serialized_practitionerroles = PractitionerRoleSerializer(
            paginated_practitionerroles, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_practitionerroles, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(description=docs.endpoints.practitioner_role.retrieve_response)
        }
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"PractitionerRole {escape(id)} not found", status=404)

        practitionerrole = get_object_or_404(self.queryset, id=id)

        serialized_practitionerrole = PractitionerRoleSerializer(
            practitionerrole, context={"request": request}
        )

        response = Response(serialized_practitionerrole.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.practitioner_role.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.practitioner_role.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.practitioner_role.default_sort}"
    )  # list description
    retrieve.__doc__ = docs.endpoints.practitioner_role.retrieve_description  # retrieve description


class FHIROrganizationViewSet(viewsets.GenericViewSet):
    queryset = OrganizationView.objects.prefetch_related(
        "authorized_official",
        "ein",
        "organization",
        "organization__organizationtoname_set",
        "organization__organizationtoaddress_set",
        "organization__organizationtoaddress_set__address",
        "organization__organizationtoaddress_set__address__address_us",
        "organization__organizationtoaddress_set__address__address_us__state_code",
        "organization__organizationtoaddress_set__address_use",
        "organization__authorized_official__individualtophone_set",
        "organization__authorized_official__individualtoname_set",
        "organization__authorized_official__individualtoemail_set",
        "organization__authorized_official__individualtoaddress_set",
        "organization__authorized_official__individualtoaddress_set__address__address_us",
        "organization__authorized_official__individualtoaddress_set__address__address_us__state_code",
        "organization__clinicalorganization",
        "organization__clinicalorganization__npi",
        "organization__clinicalorganization__organizationtootherid_set",
        "organization__clinicalorganization__organizationtootherid_set__other_id_type",
        "organization__clinicalorganization__organizationtotaxonomy_set",
        "organization__clinicalorganization__organizationtotaxonomy_set__nucc_code",
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = OrganizationFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"
    ordering = ["name"]
    ordering_fields = ["name"]

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.organization.list_response)}
    )
    def list(self, request):
        organizations = self.filter_queryset(self.queryset)
        paginated_organizations = self.paginate_queryset(organizations)

        serialized_organizations = OrganizationSerializer(
            paginated_organizations, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_organizations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.organization.retrieve_response)}
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Organization {escape(id)} not found", status=404)

        organization = get_object_or_404(
            self.queryset,
            organization_id=id,
        )

        serialized_organization = OrganizationSerializer(organization, context={"request": request})

        response = Response(serialized_organization.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.organization.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.organization.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.organization.default_sort}"
    )  # list description
    retrieve.__doc__ = docs.endpoints.organization.retrieve_description  # retrieve description


class FHIRLocationViewSet(viewsets.GenericViewSet):
    queryset = (
        Location.objects.all()
        .select_related(
            "organization",
            "address",
            "address__address_us",
            "address__address_us__state_code",
        )
        .prefetch_related(
            Prefetch(
                "organization__organizationtoaddress_set",
                queryset=OrganizationToAddress.objects.select_related(
                    "address_use", "address__address_us", "address__address_us__state_code"
                ),
            ),
        )
        .annotate(
            organization_name=F("organization__organizationtoname__name"),
            address_full=Concat(
                F("address__address_us__delivery_line_1"),
                Value(", "),
                F("address__address_us__city_name"),
                Value(", "),
                F("address__address_us__state_code__abbreviation"),
                Value(" "),
                F("address__address_us__zipcode"),
                output_field=CharField(),
            ),
        )
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = LocationFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"
    ordering = ["name"]
    ordering_fields = ["organization_name", "address_full", "name"]

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.location.list_response)}
    )
    def list(self, request):
        locations = self.filter_queryset(self.queryset)
        paginated_locations = self.paginate_queryset(locations)

        serialized_locations = LocationSerializer(
            paginated_locations, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_locations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={200: OpenApiResponse(description=docs.endpoints.location.retrieve_response)}
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Location {escape(id)} not found", status=404)

        location = get_object_or_404(self.queryset, id=id)

        serialized_location = LocationSerializer(location, context={"request": request})

        response = Response(serialized_location.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.location.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.location.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.location.default_sort}"
    )  # list description
    retrieve.__doc__ = docs.endpoints.location.retrieve_description  # retrieve description


class FHIRCapabilityStatementView(APIView):
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]

    @extend_schema(
        responses={
            200: OpenApiResponse(description=docs.endpoints.capability_statement.get_response)
        }
    )
    def get(self, request):
        serialized_capability_statement = CapabilityStatementSerializer(
            context={"request": request}
        )

        response = Response(serialized_capability_statement.to_representation())
        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.capability_statement.viewset  # endpoint description
    get.__doc__ = docs.endpoints.capability_statement.get_description  # get description


class FHIROrganizationAffiliationViewSet(viewsets.GenericViewSet):
    queryset = Organization.objects.none()
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    # filterset_class = OrganizationFilterSet
    pagination_class = CustomPaginator

    ordering = ["organization_name"]
    ordering_fields = ["ehr_vendor_name", "organization_name", "endpoint_name"]
    lookup_url_kwarg = "id"

    endpoint_subquery = LocationToEndpointInstance.objects.filter(
        location__organization=OuterRef("pk"), endpoint_instance__ehr_vendor__isnull=False
    )

    # Subquery for endpoint name (take first matching)
    endpoint_name_subquery = LocationToEndpointInstance.objects.filter(
        location__organization=OuterRef("pk"), endpoint_instance__ehr_vendor__isnull=False
    ).values("endpoint_instance__name")[:1]

    # Subquery for ehr_vendor name (take first matching)
    ehr_vendor_name_subquery = LocationToEndpointInstance.objects.filter(
        location__organization=OuterRef("pk"), endpoint_instance__ehr_vendor__isnull=False
    ).values("endpoint_instance__ehr_vendor__name")[:1]

    queryset = (
        Organization.objects.all()
        .filter(Exists(endpoint_subquery))
        .prefetch_related(
            # Clinical organization (participating org)
            "clinicalorganization",
            "clinicalorganization__npi",
            "clinicalorganization__organizationtootherid_set",
            "clinicalorganization__organizationtootherid_set__other_id_type",
            "clinicalorganization__organizationtotaxonomy_set",
            "clinicalorganization__organizationtotaxonomy_set__nucc_code",
            # --- NUCC CLASSIFICATIONS ---
            "clinicalorganization__organizationtotaxonomy_set",
            "clinicalorganization__organizationtotaxonomy_set__nucc_code",
            # --- OTHER CODE CLASSIFICATIONS ---
            "clinicalorganization__organizationtootherid_set",
            "clinicalorganization__organizationtootherid_set__other_id_type",
            # Names and addresses
            "organizationtoname_set",
            "organizationtoaddress_set",
            "organizationtoaddress_set__address",
            "organizationtoaddress_set__address__address_us",
            "organizationtoaddress_set__address__address_us__state_code",
            "organizationtoaddress_set__address_use",
            # Endpoint + vendor relationship
            "location_set",
            "location_set__locationtoendpointinstance_set",
            "location_set__locationtoendpointinstance_set__endpoint_instance",
            "location_set__locationtoendpointinstance_set__endpoint_instance__ehr_vendor",
        )
        .annotate(
            # Organization name
            organization_name=F("organizationtoname__name"),
            endpoint_name=Subquery(endpoint_name_subquery),
            ehr_vendor_name=Subquery(ehr_vendor_name_subquery),
            participating_npi=F("clinicalorganization__npi__npi"),
        )
        .distinct()
        .order_by("organization_name")
    )

    @extend_schema(
        responses={
            200: OpenApiResponse(description=docs.endpoints.organization_affiliation.list_response)
        }
    )
    def list(self, request):
        paginated_organization_affiliations = self.paginate_queryset(self.queryset)

        serialized_organization_affiliations = OrganizationAffiliationSerializer(
            paginated_organization_affiliations, many=True, context={"request": request}
        )
        bundle = BundleSerializer(
            serialized_organization_affiliations, context={"request": request}
        )

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description=docs.endpoints.organization_affiliation.retrieve_response
            )
        }
    )
    def retrieve(self, request, id=None):
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Organization {escape(id)} not found", status=404)

        organization_affiliation = get_object_or_404(
            self.queryset,
            pk=id,
        )

        serialized_organization_affiliation = OrganizationAffiliationSerializer(
            organization_affiliation, context={"request": request}
        )

        response = Response(serialized_organization_affiliation.data)

        return response

    # drf-spectacular content
    __doc__ = docs.endpoints.organization_affiliation.viewset  # endpoint description
    list.__doc__ = (
        f"{docs.endpoints.organization_affiliation.list_description}\n\n"
        f"{docs.constants.sort_order_text}{docs.endpoints.organization_affiliation.default_sort}"
    )  # list description
    retrieve.__doc__ = (
        docs.endpoints.organization_affiliation.retrieve_description
    )  # retrieve description
