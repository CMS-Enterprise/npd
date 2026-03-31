"""Experimental FastAPI server for side-by-side FHIR parity work."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import FastAPI, Request
from fastapi.openapi.docs import get_redoc_html, get_swagger_ui_html
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse

from .config import settings
from .endpoint_native_service import get_endpoint_resource, list_endpoint_resources
from .location_native_service import get_location_resource, list_location_resources
from .organization_affiliation_native_service import (
    get_organization_affiliation_resource,
    list_organization_affiliation_resources,
)
from .organization_native_service import (
    get_organization_resource,
    list_organization_resources,
)
from .pagination import build_bundle_envelope, get_page_window
from .practitioner_native_service import (
    get_practitioner_resource,
    list_practitioner_resources,
)
from .practitioner_role_native_service import (
    get_practitioner_role_resource,
    list_practitioner_role_resources,
)
from .responses import (
    FHIRJSONResponse,
    malformed_id_not_found,
    missing_uuid_not_found,
    openapi_json_response,
)

app = FastAPI(
    title="National Provider Directory API",
    description="Experimental FastAPI implementation for Django parity testing.",
    version=settings.app_version,
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
)

_CAPABILITY_STATEMENT_RESOURCES = [
    {
        "type": "Practitioner",
        "interaction": [{"code": "read"}, {"code": "search-type"}],
        "searchParam": [
            {"name": "_sort", "type": "string", "documentation": "Which field to use when ordering the results."},
            {"name": "address", "type": "string", "documentation": "Filter by any part of address. Address filter accepts websearch syntax."},
            {"name": "address_city", "type": "string", "documentation": "Filter by city name"},
            {"name": "address_postalcode", "type": "string", "documentation": "Filter by postal code/zip code"},
            {"name": "address_state", "type": "string", "documentation": "Filter by state (2-letter abbreviation)"},
            {"name": "address_use", "type": "string", "documentation": "Filter by address use type\n\n* `home` - home\n* `work` - work\n* `temp` - temp\n* `old` - old\n* `billing` - billing"},
            {"name": "gender", "type": "string", "documentation": "Filter by practitioner gender\n\n* `Female` - Female\n* `Male` - Male\n* `Other` - Other"},
            {"name": "identifier", "type": "string", "documentation": "Filter by practitioner identifier (NPI or other). Format: value or system|value"},
            {"name": "name", "type": "string", "documentation": "Filter by practitioner name (first, middle, last, or full name). Name filter accepts websearch syntax."},
            {"name": "page", "type": "integer", "documentation": "A page number within the paginated result set."},
            {"name": "page_size", "type": "integer", "documentation": "Number of results to return per page."},
            {"name": "practitioner_type", "type": "string", "documentation": "Filter by practitioner type/taxonomy. Practitioner type filter accepts websearch syntax."},
        ],
    },
    {
        "type": "Organization",
        "interaction": [{"code": "read"}, {"code": "search-type"}],
        "searchParam": [
            {"name": "_sort", "type": "string", "documentation": "Which field to use when ordering the results."},
            {"name": "address", "type": "string", "documentation": "Filter by any part of address. Address filter accepts websearch syntax."},
            {"name": "address_city", "type": "string", "documentation": "Filter by city name"},
            {"name": "address_postalcode", "type": "string", "documentation": "Filter by postal code/zip code"},
            {"name": "address_state", "type": "string", "documentation": "Filter by state (2-letter abbreviation)"},
            {"name": "address_use", "type": "string", "documentation": "Filter by address use type\n\n* `home` - home\n* `work` - work\n* `temp` - temp\n* `old` - old\n* `billing` - billing"},
            {"name": "identifier", "type": "string", "documentation": "Filter by organization identifier (NPI, EIN, or other). Format: value or system|value"},
            {"name": "name", "type": "string", "documentation": "Filter by organization name"},
            {"name": "organization_type", "type": "string", "documentation": "Filter by organization type/taxonomy"},
            {"name": "page", "type": "integer", "documentation": "A page number within the paginated result set."},
            {"name": "page_size", "type": "integer", "documentation": "Number of results to return per page."},
        ],
    },
    {
        "type": "Endpoint",
        "interaction": [{"code": "read"}, {"code": "search-type"}],
        "searchParam": [
            {"name": "_sort", "type": "string", "documentation": "Which field to use when ordering the results."},
            {"name": "connection_type", "type": "string", "documentation": "Filter by endpoint connection type"},
            {"name": "name", "type": "string", "documentation": "Filter by endpoint name"},
            {"name": "page", "type": "integer", "documentation": "A page number within the paginated result set."},
            {"name": "page_size", "type": "integer", "documentation": "Number of results to return per page."},
            {"name": "payload_type", "type": "string", "documentation": "Filter by endpoint payload type"},
            {"name": "status", "type": "string", "documentation": "Filter by endpoint status"},
        ],
    },
    {
        "type": "Location",
        "interaction": [{"code": "read"}, {"code": "search-type"}],
        "searchParam": [
            {"name": "_sort", "type": "string", "documentation": "Which field to use when ordering the results."},
            {"name": "address", "type": "string", "documentation": "Filter by any part of address. Address filter accepts websearch syntax."},
            {"name": "address_city", "type": "string", "documentation": "Filter by city name"},
            {"name": "address_postalcode", "type": "string", "documentation": "Filter by postal code/zip code"},
            {"name": "address_state", "type": "string", "documentation": "Filter by state (2-letter abbreviation)"},
            {"name": "address_use", "type": "string", "documentation": "Filter by address use type\n\n* `home` - home\n* `work` - work\n* `temp` - temp\n* `old` - old\n* `billing` - billing"},
            {"name": "name", "type": "string", "documentation": "Filter by location name"},
            {"name": "near", "type": "string", "documentation": "Filter by distance from a point expressed as [latitude]|[longitude]|[distance]|[units]. If no units are provided, km is assumed."},
            {"name": "organization_identifier", "type": "string", "documentation": "Filter by organization identifier (NPI, EIN, or other). Format: value or system|value"},
            {"name": "organization_name", "type": "string", "documentation": "Filter by organization name"},
            {"name": "organization_type", "type": "string", "documentation": "Filter by organization type/taxonomy"},
            {"name": "page", "type": "integer", "documentation": "A page number within the paginated result set."},
            {"name": "page_size", "type": "integer", "documentation": "Number of results to return per page."},
        ],
    },
    {
        "type": "PractitionerRole",
        "interaction": [{"code": "read"}, {"code": "search-type"}],
        "searchParam": [
            {"name": "_sort", "type": "string", "documentation": "Which field to use when ordering the results."},
            {"name": "active", "type": "boolean", "documentation": "Filter by active status"},
            {"name": "endpoint_connection_type", "type": "string", "documentation": "Filter by endpoint connection type"},
            {"name": "endpoint_payload_type", "type": "string", "documentation": "Filter by endpoint payload type"},
            {"name": "endpoint_status", "type": "string", "documentation": "Filter by endpoint status"},
            {"name": "location_address", "type": "string", "documentation": "Filter by any part of address. Address filter accepts websearch syntax."},
            {"name": "location_address_city", "type": "string", "documentation": "Filter by city name"},
            {"name": "location_address_postalcode", "type": "string", "documentation": "Filter by postal code/zip code"},
            {"name": "location_address_state", "type": "string", "documentation": "Filter by state (2-letter abbreviation)"},
            {"name": "location_near", "type": "string", "documentation": "Filter by distance from a point expressed as [latitude]|[longitude]|[distance]|[units]. If no units are provided, km is assumed."},
            {"name": "organization_identifier", "type": "string", "documentation": "Filter by organization identifier (NPI, EIN, or other). Format: value or system|value"},
            {"name": "organization_name", "type": "string", "documentation": "Filter by organization name"},
            {"name": "organization_type", "type": "string", "documentation": "Filter by organization type/taxonomy"},
            {"name": "page", "type": "integer", "documentation": "A page number within the paginated result set."},
            {"name": "page_size", "type": "integer", "documentation": "Number of results to return per page."},
            {"name": "practitioner_gender", "type": "string", "documentation": "Filter by practitioner gender\n\n* `Female` - Female\n* `Male` - Male\n* `Other` - Other"},
            {"name": "practitioner_identifier", "type": "string", "documentation": "Filter by practitioner identifier (NPI or other). Format: value or system|value"},
            {"name": "practitioner_name", "type": "string", "documentation": "Filter by practitioner name (first, middle, last, or full name). Name filter accepts websearch syntax."},
            {"name": "practitioner_type", "type": "string", "documentation": "Filter by practitioner type/taxonomy. Practitioner type filter accepts websearch syntax."},
            {"name": "role", "type": "string", "documentation": "Filter by provider role code"},
            {"name": "specialty", "type": "string", "documentation": "Filter by Nucc/Snomed specialty code"},
        ],
    },
]


def _resource_catalog(request: Request) -> dict[str, str]:
    return {
        "Endpoint": str(request.url_for("fhir-endpoint-list")),
        "Location": str(request.url_for("fhir-location-list")),
        "Organization": str(request.url_for("fhir-organization-list")),
        "Practitioner": str(request.url_for("fhir-practitioner-list")),
        "PractitionerRole": str(request.url_for("fhir-practitionerrole-list")),
    }


def _capability_statement(request: Request) -> dict:
    base_url = str(request.base_url).rstrip("/")
    return {
        "resourceType": "CapabilityStatement",
        "url": f"{base_url}/fhir/metadata",
        "version": "beta",
        "name": "FHIRCapablityStatement",
        "title": "NPD FHIR API -  FHIR Capablity Statement",
        "status": "active",
        "date": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ"),
        "publisher": "CMS",
        "contact": [{"telecom": [{"system": "email", "value": "npd@cms.hhs.gov"}]}],
        "description": "This CapabilityStatement describes the capabilities of the National Provider Directory FHIR API, including supported resources, search parameters, and operations.",
        "kind": "instance",
        "implementation": {
            "description": "Developers can query and retrieve National Provider Directory data via a REST API. The API structure conforms to the HL7 Fast Healthcare Interoperability Resources (FHIR) standard and it returns JSON responses following the FHIR specification.",
            "url": f"{base_url}/fhir",
        },
        "fhirVersion": "4.0.1",
        "format": ["fhir+json"],
        "rest": [
            {
                "mode": "server",
                "documentation": "All FHIR endpoints for the National Provider Directory",
                "resource": _CAPABILITY_STATEMENT_RESOURCES,
            }
        ],
    }


@app.get("/fhir", name="fhir-api-root", include_in_schema=False)
@app.get("/fhir/", include_in_schema=False)
def fhir_root(request: Request):
    return FHIRJSONResponse(_resource_catalog(request))


@app.get("/fhir/healthCheck", name="healthCheck", include_in_schema=False)
@app.get("/fhir/healthCheck/", include_in_schema=False)
def health_check():
    return PlainTextResponse("healthy")


@app.get("/fhir/docs/schema", include_in_schema=False)
@app.get("/fhir/docs/schema/", name="schema", include_in_schema=False)
def schema_json():
    return openapi_json_response(get_openapi(title=app.title, version=app.version, routes=app.routes))


@app.get("/fhir/docs", include_in_schema=False)
@app.get("/fhir/docs/", name="schema-swagger-ui", include_in_schema=False)
def swagger_ui():
    return get_swagger_ui_html(
        openapi_url="/fhir/docs/schema/",
        title=f"{app.title} - Swagger UI",
    )


@app.get("/fhir/docs/redoc", include_in_schema=False)
@app.get("/fhir/docs/redoc/", name="schema-redoc", include_in_schema=False)
def redoc_ui():
    return get_redoc_html(
        openapi_url="/fhir/docs/schema/",
        title=f"{app.title} - ReDoc",
    )


@app.get("/fhir/metadata", include_in_schema=False)
@app.get("/fhir/metadata/", name="fhir-metadata", include_in_schema=False)
def metadata(request: Request):
    return FHIRJSONResponse(_capability_statement(request))


@app.get(
    "/fhir/Endpoint",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Endpoint/",
    response_class=FHIRJSONResponse,
    name="fhir-endpoint-list",
)
def endpoint_list(request: Request):
    window = get_page_window(request)
    result = list_endpoint_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-endpoint-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/Endpoint/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Endpoint/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-endpoint-detail",
)
def endpoint_detail(id: str):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("Endpoint", id)

    resource = get_endpoint_resource(id)
    if resource is None:
        return missing_uuid_not_found("No EndpointInstance matches the given query.")

    return FHIRJSONResponse(resource)


@app.get(
    "/fhir/OrganizationAffiliation",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/OrganizationAffiliation/",
    response_class=FHIRJSONResponse,
    name="fhir-organizationaffiliation-list",
)
def organization_affiliation_list(request: Request):
    window = get_page_window(request)
    result = list_organization_affiliation_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
        base_url=str(request.base_url),
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-organizationaffiliation-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/OrganizationAffiliation/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/OrganizationAffiliation/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-organizationaffiliation-detail",
)
def organization_affiliation_detail(id: str, request: Request):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("Organization", id)

    resource = get_organization_affiliation_resource(id, base_url=str(request.base_url))
    if resource is None:
        return missing_uuid_not_found("No OrganizationAffiliationView matches the given query.")

    return FHIRJSONResponse(resource)


@app.get(
    "/fhir/Organization",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Organization/",
    response_class=FHIRJSONResponse,
    name="fhir-organization-list",
)
def organization_list(request: Request):
    window = get_page_window(request)
    result = list_organization_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
        base_url=str(request.base_url),
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-organization-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/Organization/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Organization/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-organization-detail",
)
def organization_detail(id: str, request: Request):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("Organization", id)

    resource = get_organization_resource(id, base_url=str(request.base_url))
    if resource is None:
        return missing_uuid_not_found("No OrganizationView matches the given query.")

    return FHIRJSONResponse(resource)


@app.get(
    "/fhir/PractitionerRole",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/PractitionerRole/",
    response_class=FHIRJSONResponse,
    name="fhir-practitionerrole-list",
)
def practitioner_role_list(request: Request):
    window = get_page_window(request)
    result = list_practitioner_role_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
        base_url=str(request.base_url),
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-practitionerrole-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/PractitionerRole/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/PractitionerRole/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-practitionerrole-detail",
)
def practitioner_role_detail(id: str, request: Request):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("PractitionerRole", id)

    resource = get_practitioner_role_resource(id, base_url=str(request.base_url))
    if resource is None:
        return missing_uuid_not_found("No ProviderToLocationView matches the given query.")

    return FHIRJSONResponse(resource)


@app.get(
    "/fhir/Location",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Location/",
    response_class=FHIRJSONResponse,
    name="fhir-location-list",
)
def location_list(request: Request):
    window = get_page_window(request)
    result = list_location_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
        base_url=str(request.base_url),
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-location-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/Location/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Location/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-location-detail",
)
def location_detail(id: str, request: Request):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("Location", id)

    resource = get_location_resource(id, base_url=str(request.base_url))
    if resource is None:
        return missing_uuid_not_found("No Location matches the given query.")

    return FHIRJSONResponse(resource)


@app.get(
    "/fhir/Practitioner",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Practitioner/",
    response_class=FHIRJSONResponse,
    name="fhir-practitioner-list",
)
def practitioner_list(request: Request):
    window = get_page_window(request)
    result = list_practitioner_resources(
        request.query_params,
        page=window.page,
        page_size=window.page_size,
    )
    payload = build_bundle_envelope(
        request,
        route_name="fhir-practitioner-detail",
        resources=result.resources,
        total_count=result.total_count,
        page=window.page,
        page_size=window.page_size,
    )
    return FHIRJSONResponse(payload)


@app.get(
    "/fhir/Practitioner/{id}",
    response_class=FHIRJSONResponse,
    include_in_schema=False,
)
@app.get(
    "/fhir/Practitioner/{id}/",
    response_class=FHIRJSONResponse,
    name="fhir-practitioner-detail",
)
def practitioner_detail(id: str):
    try:
        UUID(id)
    except (ValueError, TypeError):
        return malformed_id_not_found("Practitioner", id)

    resource = get_practitioner_resource(id)
    if resource is None:
        return missing_uuid_not_found("No ProviderView matches the given query.")

    return FHIRJSONResponse(resource)
