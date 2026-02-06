from django.db import models
from django.contrib.gis.db import models as geomodels


class Address(models.Model):
    id = models.UUIDField(primary_key=True)
    address_us = models.ForeignKey("AddressUs", models.DO_NOTHING, blank=True, null=True)
    address_international = models.ForeignKey(
        "AddressInternational", models.DO_NOTHING, blank=True, null=True
    )
    address_nonstandard = models.ForeignKey(
        "AddressNonstandard", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "address"


class AddressInternational(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    country_code = models.ForeignKey("IsoCountry", models.DO_NOTHING, db_column="country_code")
    geocode = models.CharField(max_length=4, blank=True, null=True)
    local_language = models.CharField(max_length=6, blank=True, null=True)
    freeform = models.CharField(max_length=512, blank=True, null=True)
    address1 = models.CharField(max_length=64)
    address2 = models.CharField(max_length=64, blank=True, null=True)
    address3 = models.CharField(max_length=64, blank=True, null=True)
    address4 = models.CharField(max_length=64, blank=True, null=True)
    organization = models.CharField(max_length=64, blank=True, null=True)
    locality = models.CharField(max_length=64, blank=True, null=True)
    administrative_area = models.CharField(max_length=32, blank=True, null=True)
    postal_code = models.CharField(max_length=16, blank=True, null=True)
    administrative_area_iso2 = models.CharField(max_length=8, blank=True, null=True)
    sub_administrative_area = models.CharField(max_length=64, blank=True, null=True)
    country_iso_3 = models.CharField(max_length=3, blank=True, null=True)
    premise = models.CharField(max_length=64, blank=True, null=True)
    premise_number = models.CharField(max_length=64, blank=True, null=True)
    thoroughfare = models.CharField(max_length=64, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    geocode_precision = models.CharField(max_length=32, blank=True, null=True)
    max_geocode_precision = models.CharField(max_length=32, blank=True, null=True)
    address_format = models.CharField(max_length=128, blank=True, null=True)
    verification_status = models.CharField(max_length=32, blank=True, null=True)
    address_precision = models.CharField(max_length=32, blank=True, null=True)
    max_address_precision = models.CharField(max_length=32, blank=True, null=True)
    geolocation = geomodels.PointField(srid=4326)

    class Meta:
        managed = False
        db_table = "address_international"


class AddressNonstandard(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    delivery_line_1 = models.CharField(max_length=64)
    delivery_line_2 = models.CharField(max_length=64, blank=True, null=True)
    last_line = models.CharField(max_length=64, blank=True, null=True)
    address_type = models.CharField(max_length=32, blank=True, null=True)
    address_format = models.CharField(max_length=128, blank=True, null=True)
    raw_address = models.TextField(blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    geolocation = geomodels.PointField(srid=4326)

    class Meta:
        managed = False
        db_table = "address_nonstandard"


class AddressUs(models.Model):
    id = models.BigIntegerField(primary_key=True)
    delivery_line_1 = models.CharField(max_length=64)
    delivery_line_2 = models.CharField(max_length=64, blank=True, null=True)
    last_line = models.CharField(max_length=64, blank=True, null=True)
    delivery_point_barcode = models.CharField(max_length=12, blank=True, null=True)
    urbanization = models.CharField(max_length=64, blank=True, null=True)
    primary_number = models.CharField(max_length=30, blank=True, null=True)
    street_name = models.CharField(max_length=64, blank=True, null=True)
    street_predirection = models.CharField(max_length=16, blank=True, null=True)
    street_postdirection = models.CharField(max_length=16, blank=True, null=True)
    street_suffix = models.CharField(max_length=16, blank=True, null=True)
    secondary_number = models.CharField(max_length=32, blank=True, null=True)
    secondary_designator = models.CharField(max_length=16, blank=True, null=True)
    extra_secondary_number = models.CharField(max_length=32, blank=True, null=True)
    extra_secondary_designator = models.CharField(max_length=16, blank=True, null=True)
    pmb_designator = models.CharField(max_length=16, blank=True, null=True)
    pmb_number = models.CharField(max_length=16, blank=True, null=True)
    city_name = models.CharField(max_length=64)
    default_city_name = models.CharField(max_length=64, blank=True, null=True)
    state_code = models.ForeignKey("FipsState", models.DO_NOTHING, db_column="state_code")
    zipcode = models.CharField(max_length=5)
    plus4_code = models.CharField(max_length=4, blank=True, null=True)
    delivery_point = models.CharField(max_length=2, blank=True, null=True)
    delivery_point_check_digit = models.CharField(max_length=1, blank=True, null=True)
    record_type = models.CharField(max_length=1, blank=True, null=True)
    zip_type = models.CharField(max_length=32, blank=True, null=True)
    county_code = models.ForeignKey(
        "FipsCounty", models.DO_NOTHING, db_column="county_code", blank=True, null=True
    )
    ews_match = models.CharField(max_length=5, blank=True, null=True)
    carrier_route = models.CharField(max_length=4, blank=True, null=True)
    congressional_district = models.CharField(max_length=2, blank=True, null=True)
    building_default_indicator = models.CharField(max_length=1, blank=True, null=True)
    rdi = models.CharField(max_length=12, blank=True, null=True)
    elot_sequence = models.CharField(max_length=4, blank=True, null=True)
    elot_sort = models.CharField(max_length=4, blank=True, null=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    coordinate_license = models.IntegerField(blank=True, null=True)
    geo_precision = models.CharField(max_length=18, blank=True, null=True)
    time_zone = models.CharField(max_length=48, blank=True, null=True)
    utc_offset = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    dst = models.CharField(max_length=5, blank=True, null=True)
    dpv_match_code = models.CharField(max_length=1, blank=True, null=True)
    dpv_footnotes = models.CharField(max_length=32, blank=True, null=True)
    dpv_cmra = models.CharField(max_length=1, blank=True, null=True)
    dpv_vacant = models.CharField(max_length=1, blank=True, null=True)
    dpv_no_stat = models.CharField(max_length=1, blank=True, null=True)
    active = models.CharField(max_length=1, blank=True, null=True)
    footnotes = models.CharField(max_length=24, blank=True, null=True)
    lacslink_code = models.CharField(max_length=2, blank=True, null=True)
    lacslink_indicator = models.CharField(max_length=1, blank=True, null=True)
    suitelink_match = models.CharField(max_length=5, blank=True, null=True)
    enhanced_match = models.CharField(max_length=64, blank=True, null=True)
    geolocation = geomodels.PointField(srid=4326)

    class Meta:
        managed = False
        db_table = "address_us"


class ClinicalOrganization(models.Model):
    organization = models.OneToOneField("Organization", models.DO_NOTHING, blank=True, null=True)
    npi = models.OneToOneField("Npi", models.DO_NOTHING, db_column="npi", primary_key=True)

    class Meta:
        managed = False
        db_table = "clinical_organization"


class CredentialType(models.Model):
    value = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "credential_type"


class DegreeType(models.Model):
    value = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "degree_type"


class EhrVendor(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200)
    is_cms_aligned_network = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "ehr_vendor"


class Endpoint(models.Model):
    id = models.UUIDField(primary_key=True)
    address = models.CharField(max_length=200)
    endpoint_type = models.ForeignKey("EndpointType", models.DO_NOTHING)
    endpoint_instance = models.ForeignKey("EndpointInstance", models.DO_NOTHING)
    name = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "endpoint"


class EndpointConnectionType(models.Model):
    id = models.CharField(primary_key=True, max_length=20)
    display = models.CharField(max_length=20)
    definition = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "endpoint_connection_type"


class EndpointInstance(models.Model):
    id = models.UUIDField(primary_key=True)
    ehr_vendor = models.ForeignKey(EhrVendor, models.DO_NOTHING)
    address = models.CharField(max_length=200)
    endpoint_connection_type = models.ForeignKey(
        EndpointConnectionType, models.DO_NOTHING, blank=True, null=True
    )
    name = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)
    environment_type = models.ForeignKey(
        "EnvironmentType", models.DO_NOTHING, blank=True, null=True
    )

    status = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "endpoint_instance"


class EndpointInstanceToOtherId(models.Model):
    pk = models.CompositePrimaryKey("endpoint_instance_id", "other_id", "issuer_id")
    endpoint_instance = models.ForeignKey(EndpointInstance, models.DO_NOTHING)
    other_id = models.CharField(max_length=100)
    system = models.CharField(max_length=200)
    issuer_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = "endpoint_instance_to_other_id"


class EndpointInstanceToPayload(models.Model):
    pk = models.CompositePrimaryKey("endpoint_instance_id", "payload_type_id")
    endpoint_instance = models.ForeignKey(EndpointInstance, models.DO_NOTHING)
    mime_type = models.ForeignKey("MimeType", models.DO_NOTHING, blank=True, null=True)
    payload_type = models.ForeignKey("PayloadType", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "endpoint_instance_to_payload"


class EndpointInstanceType(models.Model):
    value = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "endpoint_instance_type"


class EndpointToOtherId(models.Model):
    pk = models.CompositePrimaryKey("endpoint_id", "other_id", "issuer_id")
    endpoint = models.ForeignKey(Endpoint, models.DO_NOTHING)
    other_id = models.CharField(max_length=100)
    system = models.CharField(max_length=200)
    issuer_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = "endpoint_to_other_id"


class EndpointToPayload(models.Model):
    pk = models.CompositePrimaryKey("endpoint_id", "payload_type_id")
    endpoint = models.ForeignKey(Endpoint, models.DO_NOTHING)
    mime_type = models.ForeignKey("MimeType", models.DO_NOTHING, blank=True, null=True)
    payload_type = models.ForeignKey("PayloadType", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "endpoint_to_payload"


class EndpointType(models.Model):
    value = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "endpoint_type"


class EnvironmentType(models.Model):
    id = models.CharField(primary_key=True, max_length=10)
    display = models.CharField(max_length=20)
    definition = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "environment_type"


class FhirAddressUse(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fhir_address_use"


class FhirEmailUse(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fhir_email_use"


class FhirNameUse(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fhir_name_use"


class FhirPhoneSystem(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fhir_phone_system"


class FhirPhoneUse(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "fhir_phone_use"


class FipsCounty(models.Model):
    id = models.CharField(primary_key=True, max_length=5)
    name = models.CharField(max_length=200)
    fips_state = models.ForeignKey("FipsState", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "fips_county"
        unique_together = (("name", "fips_state"),)


class FipsState(models.Model):
    id = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(unique=True, max_length=100)
    abbreviation = models.CharField(unique=True, max_length=2)

    class Meta:
        managed = False
        db_table = "fips_state"


class Individual(models.Model):
    id = models.UUIDField(primary_key=True)
    ssn_id = models.UUIDField(blank=True, null=True)
    gender = models.CharField(max_length=1, blank=True, null=True)
    sex = models.CharField(max_length=1, blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "individual"


class IndividualToAddress(models.Model):
    pk = models.CompositePrimaryKey("individual_id", "address_id", "address_use_id")
    individual = models.ForeignKey(Individual, models.DO_NOTHING)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    address_use = models.ForeignKey(FhirAddressUse, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "individual_to_address"


class IndividualToEmail(models.Model):
    pk = models.CompositePrimaryKey("individual_id", "email_address", "email_use_id")
    individual = models.ForeignKey(Individual, models.DO_NOTHING)
    email_address = models.CharField(max_length=1000)
    email_use = models.ForeignKey(FhirEmailUse, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "individual_to_email"


class IndividualToLanguageSpoken(models.Model):
    pk = models.CompositePrimaryKey("individual_id", "language_spoken_id")
    language_spoken = models.ForeignKey("LanguageSpoken", models.DO_NOTHING)
    individual_id = models.UUIDField()

    class Meta:
        managed = False
        db_table = "individual_to_language_spoken"


class IndividualToName(models.Model):
    pk = models.CompositePrimaryKey("individual_id", "first_name", "last_name", "name_use_id")
    individual = models.ForeignKey(Individual, models.DO_NOTHING)
    prefix = models.CharField(max_length=10, blank=True, null=True)
    first_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=200)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    name_use = models.ForeignKey(FhirNameUse, models.DO_NOTHING)
    suffix = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "individual_to_name"


class IndividualToPhone(models.Model):
    individual = models.ForeignKey(Individual, models.DO_NOTHING)
    phone_number = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True, null=True)
    phone_use = models.ForeignKey(FhirPhoneUse, models.DO_NOTHING)
    id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = "individual_to_phone"
        unique_together = (("individual", "phone_number", "phone_use"),)


class IsoCountry(models.Model):
    code = models.CharField(primary_key=True, max_length=2)
    name = models.CharField(unique=True, max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "iso_country"


class LanguageSpoken(models.Model):
    id = models.CharField(primary_key=True, max_length=2)
    value = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "language_spoken"


class LegalEntity(models.Model):
    ein_id = models.UUIDField(primary_key=True)
    dba_name = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "legal_entity"


class Location(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=200, blank=True, null=True)
    organization = models.ForeignKey("Organization", models.DO_NOTHING)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    active = models.BooleanField(blank=True, null=True)
    phone = models.ForeignKey("OrganizationToPhone", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "location"


class LocationToEndpointInstance(models.Model):
    pk = models.CompositePrimaryKey("location_id", "endpoint_instance_id")
    location = models.ForeignKey(Location, models.DO_NOTHING)
    endpoint_instance = models.ForeignKey(EndpointInstance, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "location_to_endpoint_instance"


class MedicareProviderType(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "medicare_provider_type"


class MimeType(models.Model):
    value = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "mime_type"


class Npi(models.Model):
    npi = models.BigIntegerField(primary_key=True)
    entity_type_code = models.SmallIntegerField()
    replacement_npi = models.BigIntegerField(blank=True, null=True)
    enumeration_date = models.DateField()
    last_update_date = models.DateField()
    deactivation_reason_code = models.CharField(max_length=3, blank=True, null=True)
    deactivation_date = models.DateField(blank=True, null=True)
    reactivation_date = models.DateField(blank=True, null=True)
    certification_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "npi"


class Nucc(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    display_name = models.TextField()
    definition = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    certifying_board_name = models.TextField(blank=True, null=True)
    certifying_board_url = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nucc"


class NuccClassification(models.Model):
    nucc_code = models.ForeignKey(
        Nucc, models.DO_NOTHING, db_column="nucc_code", blank=True, null=True
    )
    display_name = models.CharField(max_length=100, blank=True, null=True)
    nucc_grouping = models.ForeignKey("NuccGrouping", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nucc_classification"
        unique_together = (("nucc_code", "nucc_grouping"),)


class NuccGrouping(models.Model):
    display_name = models.CharField(unique=True, max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nucc_grouping"


class NuccSpecialization(models.Model):
    nucc_code = models.ForeignKey(
        Nucc, models.DO_NOTHING, db_column="nucc_code", blank=True, null=True
    )
    display_name = models.CharField(max_length=100, blank=True, null=True)
    nucc_classification_id = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "nucc_specialization"
        unique_together = (("nucc_code", "nucc_classification_id"),)


class NuccToMedicareProviderType(models.Model):
    pk = models.CompositePrimaryKey("medicare_provider_type_id", "nucc_code")
    medicare_provider_type = models.ForeignKey(MedicareProviderType, models.DO_NOTHING)
    nucc_code = models.ForeignKey(Nucc, models.DO_NOTHING, db_column="nucc_code")

    class Meta:
        managed = False
        db_table = "nucc_to_medicare_provider_type"


class Organization(models.Model):
    id = models.UUIDField(primary_key=True)
    authorized_official = models.ForeignKey(Individual, models.DO_NOTHING, blank=True, null=True)
    ein = models.ForeignKey(LegalEntity, models.DO_NOTHING, blank=True, null=True)
    parent = models.ForeignKey("self", models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "organization"


class OrganizationToAddress(models.Model):
    pk = models.CompositePrimaryKey("organization_id", "address_id", "address_use_id")
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    address = models.ForeignKey(Address, models.DO_NOTHING)
    address_use = models.ForeignKey(FhirAddressUse, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "organization_to_address"


class OrganizationToName(models.Model):
    pk = models.CompositePrimaryKey("organization_id", "name")
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    name = models.CharField(max_length=1000)
    is_primary = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "organization_to_name"


class OrganizationToOtherId(models.Model):
    pk = models.CompositePrimaryKey("npi", "other_id", "other_id_type_id", "issuer", "state_code")
    npi = models.ForeignKey(ClinicalOrganization, models.DO_NOTHING, db_column="npi")
    other_id = models.CharField(max_length=100)
    other_id_type = models.ForeignKey("OtherIdType", models.DO_NOTHING)
    state_code = models.CharField(max_length=2)
    issuer = models.CharField(max_length=200)

    class Meta:
        managed = False
        db_table = "organization_to_other_id"


class OrganizationToPhone(models.Model):
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    phone_number = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True, null=True)
    phone_use = models.ForeignKey(FhirPhoneUse, models.DO_NOTHING)
    id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = "organization_to_phone"
        unique_together = (("organization", "phone_number", "extension", "phone_use"),)


class OrganizationToTaxonomy(models.Model):
    pk = models.CompositePrimaryKey("npi", "nucc_code")
    npi = models.ForeignKey(ClinicalOrganization, models.DO_NOTHING, db_column="npi")
    nucc_code = models.ForeignKey(Nucc, models.DO_NOTHING, db_column="nucc_code")
    is_primary = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "organization_to_taxonomy"


class OtherIdType(models.Model):
    value = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "other_id_type"


class PayloadType(models.Model):
    id = models.CharField(primary_key=True, max_length=100)
    value = models.CharField(max_length=200, blank=True, null=True)
    description = models.CharField(max_length=1000, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "payload_type"


class Provider(models.Model):
    npi = models.OneToOneField(Npi, models.DO_NOTHING, db_column="npi")
    individual = models.OneToOneField(Individual, models.DO_NOTHING, primary_key=True)

    class Meta:
        managed = False
        db_table = "provider"


class ProviderEducation(models.Model):
    pk = models.CompositePrimaryKey("npi", "school_id")
    npi = models.ForeignKey(Provider, models.DO_NOTHING, db_column="npi", to_field="npi")
    school_id = models.IntegerField()
    degree_type = models.ForeignKey(DegreeType, models.DO_NOTHING)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "provider_education"


class ProviderRole(models.Model):
    code = models.CharField(primary_key=True, max_length=10)
    system = models.CharField(max_length=100)
    display = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "provider_role"


class ProviderToCredential(models.Model):
    pk = models.CompositePrimaryKey(
        "provider_to_taxonomy_id", "credential_type_id", "license_number", "state_code"
    )
    credential_type = models.ForeignKey(CredentialType, models.DO_NOTHING)
    license_number = models.CharField(max_length=20)
    state_code = models.ForeignKey(FipsState, models.DO_NOTHING, db_column="state_code")
    provider_to_taxonomy = models.ForeignKey("ProviderToTaxonomy", models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = "provider_to_credential"


class ProviderToLocation(models.Model):
    location = models.ForeignKey(Location, models.DO_NOTHING)
    other_address = models.ForeignKey(Address, models.DO_NOTHING, blank=True, null=True)
    nucc_code = models.IntegerField(blank=True, null=True)
    specialty_id = models.IntegerField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)
    provider_role_code = models.CharField(max_length=10, blank=True, null=True)
    other_phone = models.ForeignKey(IndividualToPhone, models.DO_NOTHING, blank=True, null=True)
    other_endpoint = models.ForeignKey(Endpoint, models.DO_NOTHING, blank=True, null=True)
    active = models.BooleanField(blank=True, null=True)
    provider_to_organization = models.ForeignKey(
        "ProviderToOrganization", models.DO_NOTHING, blank=True, null=True
    )

    class Meta:
        managed = False
        db_table = "provider_to_location"


class ProviderToOrganization(models.Model):
    individual = models.ForeignKey(Provider, models.DO_NOTHING)
    organization = models.ForeignKey(Organization, models.DO_NOTHING)
    relationship_type = models.ForeignKey("RelationshipType", models.DO_NOTHING)
    id = models.UUIDField(primary_key=True)
    active = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "provider_to_organization"
        unique_together = (("individual", "organization", "relationship_type"),)


class ProviderToOtherId(models.Model):
    pk = models.CompositePrimaryKey("npi", "other_id", "other_id_type_id", "issuer", "state_code")
    npi = models.ForeignKey(Provider, models.DO_NOTHING, db_column="npi", to_field="npi")
    other_id = models.CharField(max_length=100)
    other_id_type = models.ForeignKey(OtherIdType, models.DO_NOTHING)
    state_code = models.ForeignKey(FipsState, models.DO_NOTHING, db_column="state_code")
    issuer = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = "provider_to_other_id"


class ProviderToTaxonomy(models.Model):
    npi = models.ForeignKey(Provider, models.DO_NOTHING, db_column="npi", to_field="npi")
    nucc_code = models.ForeignKey(Nucc, models.DO_NOTHING, db_column="nucc_code")
    is_primary = models.BooleanField(blank=True, null=True)
    id = models.UUIDField(primary_key=True)

    class Meta:
        managed = False
        db_table = "provider_to_taxonomy"
        unique_together = (("npi", "nucc_code"),)


class RelationshipType(models.Model):
    value = models.CharField(unique=True, max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "relationship_type"
