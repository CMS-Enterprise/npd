import uuid

from ...models import (
    EhrVendor,
    Endpoint,
    EndpointInstance,
    EndpointInstanceToPayload,
)
from .organization import create_organization


def create_endpoint_instance(
    organization=None,
    url="https://example.org/fhir",
    name="Test Endpoint",
    ehr=None,
    payload_type="any",
    endpoint_connection_type="hl7-fhir-rest",
):
    """
    Creates EndpointType, EndpointConnectionType, EndpointInstance, Endpoint.
    """
    organization = organization or create_organization()

    if not ehr:
        new_vendor_id = uuid.uuid4()
        ehr_vendor = EhrVendor.objects.create(
            id=new_vendor_id, name=f"My Sample{new_vendor_id}", is_cms_aligned_network=True
        )
    else:
        ehr_vendor = ehr

    instance = EndpointInstance.objects.create(
        id=uuid.uuid4(),
        ehr_vendor_id=ehr_vendor.id,
        address=url,
        endpoint_connection_type_id=endpoint_connection_type,
        name=name,
        environment_type_id="prod",
    )

    EndpointInstanceToPayload.objects.create(
        endpoint_instance=instance, payload_type_id=payload_type
    )

    return instance
