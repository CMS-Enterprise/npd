"""Response helpers for FHIR and docs endpoints."""

from __future__ import annotations

from html import escape
import json

from fastapi.encoders import jsonable_encoder
from fastapi.responses import HTMLResponse, JSONResponse


FHIR_MEDIA_TYPE = "application/fhir+json"
OPENAPI_MEDIA_TYPE = "application/vnd.oai.openapi+json"


class FHIRJSONResponse(JSONResponse):
    media_type = FHIR_MEDIA_TYPE

    def render(self, content) -> bytes:
        return json.dumps(
            jsonable_encoder(content),
            ensure_ascii=False,
            allow_nan=False,
            separators=(",", ":"),
        ).encode("utf-8")


def malformed_id_not_found(resource_type: str, resource_id: str) -> HTMLResponse:
    return HTMLResponse(
        content=f"{resource_type} {escape(resource_id)} not found",
        status_code=404,
        media_type="text/html",
    )


def missing_uuid_not_found(detail: str) -> FHIRJSONResponse:
    return FHIRJSONResponse({"detail": detail}, status_code=404)


def openapi_json_response(payload: dict) -> JSONResponse:
    return JSONResponse(payload, media_type=OPENAPI_MEDIA_TYPE)
