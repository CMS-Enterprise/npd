import uuid

from ...models import (
    EhrVendor,
    EndpointInstance,
    EndpointInstanceToPayload,
)


class DefaultEhrVendor:
    def __init__(self, id: uuid, name: str = "EHR Vendor"):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        self.name = name
        self.create_if_not_exists()

    def create_if_not_exists(self):
        ehr_vendor = EhrVendor.objects.filter(id=self.id)
        if ehr_vendor.exists():
            self.ehr_vendor = ehr_vendor.first()
        else:
            self.ehr_vendor = EhrVendor.objects.create(id=self.id, name=self.name)
        return self.ehr_vendor


class DefaultEndpointInstance:
    def __init__(
        self,
        id: uuid,
        ehr_vendor: DefaultEhrVendor,
        address: str = "https://example.org/fhir",
        name: str = "FHIR Endpoint",
        payload_type: str = "any",
        endpoint_connection_type: str = "hl7-fhir-rest",
        environment_type: str = "prod",
    ):
        if id is None:
            self.id = uuid.uuid4()
        else:
            self.id = id
        if ehr_vendor is None:
            ehr_vendor = DefaultEhrVendor()
        self.ehr_vendor = ehr_vendor
        self.adddress = address
        self.name = name
        self.payload_type = payload_type
        self.endpoint_connection_type = endpoint_connection_type
        self.environment_type = environment_type
        self.create_if_not_exists()

    def create_if_not_exists(self):
        endpoint_instance = EndpointInstance.objects.filter(id=self.id)
        if endpoint_instance.exists():
            self.endpoint_instance = endpoint_instance.first()
        else:
            self.endpoint_instance = EndpointInstance.objects.create(
                id=self.id,
                ehr_vendor_id=self.ehr_vendor.id,
                address=self.address,
                endpoint_connection_type_id=self.endpoint_connection_type,
                name=self.name,
                environment_type_id="prod",
            )
            EndpointInstanceToPayload.objects.create(
                endpoint_instance_id=self.id, payload_type_id=self.payload_type
            )
        return self.endpoint_instance
