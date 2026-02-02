from uuid import UUID

from django.conf import settings
from django.db.models import CharField, F, Value, Prefetch
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
    Organization,
    Provider,
    ProviderToLocation,
    OrganizationToAddress,
)

from .serializers import (
    BundleSerializer,
    EndpointSerializer,
    LocationSerializer,
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
    """
    ViewSet for FHIR Endpoint Resources
    """

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
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR Bundle resource of FHIR Endpoint resources"
            )
        }
    )
    def list(self, request):
        """
        Query a list of interoperability endpoints, represented as a bundle of FHIR Endpoint resources

        Default sort order: ascending endpoint instance name
        """

        endpoints = self.filter_queryset(self.queryset)
        paginated_endpoints = self.paginate_queryset(endpoints)

        serialized_endpoints = EndpointSerializer(
            paginated_endpoints, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_endpoints, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Successfully retrieved FHIR Endpoint resource")
        }
    )
    def retrieve(self, request, id=None):
        """
        Query a specific endpoint as a FHIR Endpoint resource
        """

        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Endpoint {escape(id)} not found", status=404)

        endpoint = get_object_or_404(
            self.queryset,
            id=id,
        )

        serialized_endpoint = EndpointSerializer(endpoint, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = Response(serialized_endpoint.data)

        return response


class FHIRPractitionerViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Practitioner resources
    """

    queryset = Provider.objects.all().prefetch_related(
        "npi",
        "individual",
        "individual__individualtoaddress_set",
        "individual__individualtoaddress_set__address__address_us",
        "individual__individualtoaddress_set__address__address_us__state_code",
        "individual__individualtoaddress_set__address_use",
        "individual__individualtophone_set",
        "individual__individualtoemail_set",
        "individual__individualtoname_set",
        "providertootherid_set__other_id_type",
        "providertotaxonomy_set",
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
        "individual__individualtoname__last_name",
        "individual__individualtoname__first_name",
    ]

    ordering_fields = [
        "individual__individualtoname__last_name",
        "individual__individualtoname__first_name",
        "npi_value",
    ]

    # permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR Bundle resource of FHIR Practitioner resources"
            )
        }
    )
    def list(self, request):
        """
        Query a list of healthcare providers, represented as a bundle of FHIR Practitioner resources

        Default sort order: ascending last name, first name
        """
        # Subqueries for last_name and first_name of the individual

        providers = self.filter_queryset(self.queryset)
        paginated_providers = self.paginate_queryset(providers)

        serialized_providers = PractitionerSerializer(paginated_providers, many=True)
        bundle = BundleSerializer(serialized_providers, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Successfully retrieved FHIR Practitioner resource")
        }
    )
    def retrieve(self, request, id=None):
        """
        Query a specific provider as a FHIR Practitioner resource
        """
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Practitioner {escape(id)} not found", status=404)

        provider = get_object_or_404(
            self.queryset,
            individual_id=id,
        )

        serialized_practitioner = PractitionerSerializer(provider)

        # Set appropriate content type for FHIR responses
        response = Response(serialized_practitioner.data)

        return response


class FHIRPractitionerRoleViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR PractitionerRole resources

    """

    queryset = (
        ProviderToLocation.objects.all()
        .select_related("location")
        .prefetch_related("provider_to_organization")
        .annotate(location_name=F("location__name"))
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = PractitionerRoleFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"

    ordering = ["location__name"]
    ordering_fields = ["location__name", "practitioner_first_name", "practitioner_last_name"]

    # permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR Bundle resource of FHIR PractitionerRole resources"
            )
        }
    )
    def list(self, request):
        """
        Query a list of relationships between providers, healthcare organizations, and practice locations, represented as a bundle of FHIR PractitionerRole resources

        Default sort order: aschending by location name
        """
        # all_params = request.query_params

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
            200: OpenApiResponse(
                description="Successfully retrieved FHIR PractitionerRole resource"
            )
        }
    )
    def retrieve(self, request, id=None):
        """
        Query a specific relationship between providers, healthcare organizations, and practice locations, represented as a FHIR PractitionerRole resource
        """
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"PractitionerRole {escape(id)} not found", status=404)

        practitionerrole = get_object_or_404(self.queryset, id=id)

        serialized_practitionerrole = PractitionerRoleSerializer(
            practitionerrole, context={"request": request}
        )

        # Set appropriate content type for FHIR responses
        response = Response(serialized_practitionerrole.data)

        return response


class FHIROrganizationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Organization resources
    """

    queryset = Organization.objects.all().prefetch_related(
        "authorized_official",
        "ein",
        "organizationtoname_set",
        "organizationtoaddress_set",
        "organizationtoaddress_set__address",
        "organizationtoaddress_set__address__address_us",
        "organizationtoaddress_set__address__address_us__state_code",
        "organizationtoaddress_set__address_use",
        "authorized_official__individualtophone_set",
        "authorized_official__individualtoname_set",
        "authorized_official__individualtoemail_set",
        "authorized_official__individualtoaddress_set",
        "authorized_official__individualtoaddress_set__address__address_us",
        "authorized_official__individualtoaddress_set__address__address_us__state_code",
        "clinicalorganization",
        "clinicalorganization__npi",
        "clinicalorganization__organizationtootherid_set",
        "clinicalorganization__organizationtootherid_set__other_id_type",
        "clinicalorganization__organizationtotaxonomy_set",
        "clinicalorganization__organizationtotaxonomy_set__nucc_code",
    )
    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]
    filter_backends = [DjangoFilterBackend, ParamOrderingFilter]
    filterset_class = OrganizationFilterSet
    pagination_class = CustomPaginator
    lookup_url_kwarg = "id"
    ordering = ["organizationtoname__name"]
    ordering_fields = ["organizationtoname__name"]

    # permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR Bundle resource of FHIR Organization resources"
            )
        }
    )
    def list(self, request):
        """
        Query a list of organizations, represented as a bundle of FHIR Practitioner resources

        Default sort order: ascending by organization name
        """

        organizations = self.filter_queryset(self.queryset)
        paginated_organizations = self.paginate_queryset(organizations)

        serialized_organizations = OrganizationSerializer(
            paginated_organizations, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_organizations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Successfully retrieved FHIR Organization resource")
        }
    )
    def retrieve(self, request, id=None):
        """
        Query a specific organization, represented as a FHIR Organization resource
        """
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Organization {escape(id)} not found", status=404)

        organization = get_object_or_404(
            self.queryset,
            id=id,
        )

        serialized_organization = OrganizationSerializer(organization, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = Response(serialized_organization.data)

        return response


class FHIRLocationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for FHIR Location resources
    """

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

    # permission_classes = [permissions.IsAuthenticated]
    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR Bundle resource of FHIR Location resources"
            )
        }
    )
    def list(self, request):
        """
        Query a list of healthcare practice locations, represented as bundle of FHIR Location resources

        Default sort order: ascending by location name
        """
        locations = self.filter_queryset(self.queryset)
        paginated_locations = self.paginate_queryset(locations)

        # Serialize the bundle
        serialized_locations = LocationSerializer(
            paginated_locations, many=True, context={"request": request}
        )
        bundle = BundleSerializer(serialized_locations, context={"request": request})

        response = self.get_paginated_response(bundle.data)
        return response

    @extend_schema(
        responses={
            200: OpenApiResponse(description="Successfully retrieved FHIR Location resource")
        }
    )
    def retrieve(self, request, id=None):
        """
        Query a specific healthcare practice location as a FHIR Location resource
        """
        try:
            UUID(id)
        except (ValueError, TypeError):
            return HttpResponse(f"Location {escape(id)} not found", status=404)

        location = get_object_or_404(self.queryset, id=id)

        serialized_location = LocationSerializer(location, context={"request": request})

        # Set appropriate content type for FHIR responses
        response = Response(serialized_location.data)

        return response


class FHIRCapabilityStatementView(APIView):
    """
    ViewSet for FHIR Practitioner resources
    """

    if DEBUG:
        renderer_classes = [FHIRRenderer, BrowsableAPIRenderer]
    else:
        renderer_classes = [FHIRRenderer]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                description="Successfully retrieved FHIR CapabilityStatement resource"
            )
        }
    )
    def get(self, request):
        """
        Query metadata about this FHIR instance, represented as FHIR CapabilityStatement resource
        """
        serialized_capability_statement = CapabilityStatementSerializer(
            context={"request": request}
        )

        response = Response(serialized_capability_statement.to_representation())

        return response
