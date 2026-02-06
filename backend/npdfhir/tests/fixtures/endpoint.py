import uuid

from ...models import (
    EhrVendor,
    Endpoint,
    EndpointConnectionType,
    EndpointInstance,
    EndpointInstanceToPayload,
    EndpointType,
    PayloadType,
)
from .organization import create_organization


def _ensure_endpoint_base_types():
    """
    Flyway inserts some reference values, but ensure minimal ones exist.
    """
    etype, _ = EndpointType.objects.get_or_create(value="rest")
    ctype, _ = EndpointConnectionType.objects.get_or_create(
        id="hl7-fhir-rest",
        defaults={"display": "FHIR REST", "definition": "FHIR REST endpoint"},
    )
    payload, _ = PayloadType.objects.get_or_create(
        id="fhir-json",
        defaults={"value": "application/fhir+json", "description": "FHIR JSON"},
    )
    return etype, ctype, payload


def create_endpoint(
    organization=None,
    url="https://example.org/fhir",
    name="Test Endpoint",
    ehr=None,
    payload_type=None,
):
    """
    Creates EndpointType, EndpointConnectionType, EndpointInstance, Endpoint.
    """
    organization = organization or create_organization()

    etype, ctype, payload = _ensure_endpoint_base_types()

    if not ehr:
        new_vendor_id = uuid.uuid4()
        ehr_vendor = EhrVendor.objects.create(
            id=new_vendor_id, name=f"My Sample{new_vendor_id}", is_cms_aligned_network=True
        )
    else:
        ehr_vendor = ehr

    pt = PayloadType.objects.get(pk=payload_type or "urn:hl7-org:sdwg:ccda-structuredBody:1.1")

    instance = EndpointInstance.objects.create(
        id=uuid.uuid4(),
        ehr_vendor_id=ehr_vendor.id,
        address=url,
        endpoint_connection_type=ctype,
        name=name,
        environment_type_id="prod",
    )

    EndpointInstanceToPayload.objects.create(endpoint_instance=instance, payload_type=pt)

    ep = Endpoint.objects.create(
        id=uuid.uuid4(),
        address=url,
        endpoint_type=etype,
        endpoint_instance=instance,
        name=name,
    )

    return ep
