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
from .organization_affiliation_service import (
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
from .practitioner_role_service import (
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
        "url": f"{base_url}/fhir/metadata/",
        "version": settings.app_version,
        "name": "FHIRCapabilityStatement",
        "title": "National Provider Directory API - FHIR Capability Statement",
        "status": "active",
        "date": datetime.now(timezone.utc).isoformat(),
        "publisher": "CMS",
        "description": "Experimental FastAPI CapabilityStatement used for parity development.",
        "kind": "instance",
        "fhirVersion": "4.0.1",
        "format": ["fhir+json"],
        "rest": [
            {
                "mode": "server",
                "documentation": "Experimental FastAPI FHIR endpoints for parity testing.",
                "resource": [
                    {
                        "type": "Endpoint",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [
                            {"name": "name", "type": "string"},
                            {"name": "connection_type", "type": "string"},
                            {"name": "payload_type", "type": "string"},
                            {"name": "status", "type": "string"},
                        ],
                    },
                    {
                        "type": "Location",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [
                            {"name": "name", "type": "string"},
                            {"name": "organization_name", "type": "string"},
                            {"name": "organization_identifier", "type": "string"},
                            {"name": "organization_type", "type": "string"},
                            {"name": "address", "type": "string"},
                            {"name": "address_city", "type": "string"},
                            {"name": "address_state", "type": "string"},
                            {"name": "address_postalcode", "type": "string"},
                            {"name": "address_use", "type": "string"},
                            {"name": "near", "type": "string"},
                        ],
                    },
                    {
                        "type": "Organization",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [
                            {"name": "name", "type": "string"},
                            {"name": "identifier", "type": "string"},
                            {"name": "organization_type", "type": "string"},
                            {"name": "address", "type": "string"},
                            {"name": "address_city", "type": "string"},
                            {"name": "address_state", "type": "string"},
                            {"name": "address_postalcode", "type": "string"},
                            {"name": "address_use", "type": "string"},
                        ],
                    },
                    {
                        "type": "Practitioner",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [
                            {"name": "identifier", "type": "string"},
                            {"name": "name", "type": "string"},
                            {"name": "gender", "type": "string"},
                            {"name": "practitioner_type", "type": "string"},
                            {"name": "address", "type": "string"},
                            {"name": "address_city", "type": "string"},
                            {"name": "address_state", "type": "string"},
                            {"name": "address_postalcode", "type": "string"},
                            {"name": "address_use", "type": "string"},
                        ],
                    },
                    {
                        "type": "PractitionerRole",
                        "interaction": [{"code": "read"}, {"code": "search-type"}],
                        "searchParam": [
                            {"name": "practitioner_name", "type": "string"},
                            {"name": "practitioner_gender", "type": "string"},
                            {"name": "practitioner_type", "type": "string"},
                            {"name": "practitioner_identifier", "type": "string"},
                            {"name": "organization_name", "type": "string"},
                            {"name": "organization_type", "type": "string"},
                            {"name": "organization_identifier", "type": "string"},
                            {"name": "location_near", "type": "string"},
                            {"name": "location_address", "type": "string"},
                            {"name": "location_address_city", "type": "string"},
                            {"name": "location_address_state", "type": "string"},
                            {"name": "location_address_postalcode", "type": "string"},
                            {"name": "active", "type": "string"},
                            {"name": "role", "type": "string"},
                            {"name": "specialty", "type": "string"},
                            {"name": "endpoint_connection_type", "type": "string"},
                            {"name": "endpoint_payload_type", "type": "string"},
                            {"name": "endpoint_status", "type": "string"},
                        ],
                    }
                ],
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
