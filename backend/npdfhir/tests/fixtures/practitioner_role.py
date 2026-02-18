def create_full_practitionerrole(
    first_name="Alice",
    last_name="Smith",
    gender="F",
    npi_value=None,
    org_name="Test Org",
    location_id=None,
    role_code="PRV",
    role_display="Provider Role",
    practitioner_nucc_types=None,
    organization_nucc_type=None,
    location_city=None,
    location_state=None,
    location_zip=None,
    endpoint_payload_type="any",
    endpoint_connection_type=None,
    specialty_id=None,
):
    """
    Creates:
        Practitioner (Provider)
        Organization
        Location
        ProviderToOrganization
        ProviderToLocation
    """
    provider = create_practitioner(
        first_name=first_name,
        last_name=last_name,
        gender=gender,
        npi_value=npi_value,
        practitioner_types=practitioner_nucc_types,
    )
    org = create_organization(name=org_name, organization_type=organization_nucc_type)
    if location_id is None:
        loc = create_location(
            city=location_city, zipcode=location_zip, state=location_state, organization=org
        )
        location_id = loc.id

    # Ensure relationship + role codes exist
    rel_type = _ensure_relationship_type()
    _ensure_provider_role(role_code, role_display)

    pto_org = ProviderToOrganization.objects.create(
        id=uuid.uuid4(),
        individual=provider,  # special FK uses Provider.individual_id
        organization=org,
        relationship_type=rel_type,
        active=True,
    )

    endpoint_instance = create_endpoint_instance(
        organization=org,
        url="https://example.org/fhir",
        name="Test Endpoint",
        ehr=None,
        payload_type=endpoint_payload_type,
        endpoint_connection_type=endpoint_connection_type,
    )

    LocationToEndpointInstance.objects.create(
        location_id=location_id, endpoint_instance_id=endpoint_instance.id
    )

    pr = ProviderToLocation.objects.create(
        id=uuid.uuid4(),
        provider_to_organization=pto_org,
        location_id=location_id,
        provider_role_code=role_code,
        active=True,
        specialty_id=specialty_id,
    )

    return pr
