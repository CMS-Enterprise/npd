from django.urls import reverse
from fhir.resources.R4B.address import Address
from fhir.resources.R4B.reference import Reference
from drf_spectacular.views import SpectacularJSONAPIView


def SmartyStreetstoFHIR(address):
    addressLine1 = f"{address.address_us.primary_number} {address.address_us.street_predirection} {address.address_us.street_name} {address.address_us.postdirection} {address.address_us.street_suffix}"
    addressLine2 = (
        f"{address.address_us.secondary_designator} {address.address_us.secondary_number}"
    )
    addressLine3 = f"{address.address_us.extra_secondary_designator} {address.address_us.extra_secondary_number}"
    cityStateZip = f"f{address.address_us.city_name}, {address.address_us.fips_state.state_abbreviation} {address.address_us.zipcode}"
    return Address(
        line=[addressLine1, addressLine2, addressLine3, cityStateZip],
        use=address.address_type.value,
    )


def get_schema_data(request):
    schema_view = SpectacularJSONAPIView.as_view()
    response = schema_view(request._request)
    # The response contains the schema data in its .data attribute
    schema_data = response.data

    return schema_data


def genReference(url_name, identifier, request):
    reference = request.build_absolute_uri(reverse(url_name, kwargs={"id": identifier}))
    reference = Reference(reference=reference)
    return reference


def parse_identifier_query(identifier_value):
    """
    Parse an identifier search parameter that should be in the format of "value" OR "system|value".
    Currently only supporting NPI search "NPI|123455".
    """
    if "|" in identifier_value:
        parts = identifier_value.split("|", 1)
        return (parts[0], parts[1])

    return (None, identifier_value)
