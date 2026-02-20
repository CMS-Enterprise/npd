from django.utils.translation import gettext_lazy as _


class docs:
    # Centralized namespace for all NPD API documentation content

    class constants:
        # Constant strings that appear throughout content building

        sort_order_text = _("Default sort order: ")

    class filters:
        # Help text for filter parameters, organized by FHIR resource

        class practitioner:
            name = _(
                "Filter by practitioner name (first, middle, last, or full name). "
                "Name filter accepts websearch syntax."
            )
            gender = _("Filter by practitioner gender")
            identifier = _(
                "Filter by practitioner identifier (NPI or other). Format: value or system|value"
            )
            type = _(
                "Filter by practitioner type/taxonomy. "
                "Practitioner type filter accepts websearch syntax."
            )

        class organization:
            name = _("Filter by organization name")
            identifier = _(
                "Filter by organization identifier (NPI, EIN, or other). "
                "Format: value or system|value"
            )
            type = _("Filter by organization type/taxonomy")

        class location:
            name = _("Filter by location name")
            near = _(
                "Filter by distance from a point expressed as "
                "[latitude]|[longitude]|[distance]|[units]. "
                "If no units are provided, km is assumed."
            )

        class endpoint:
            name = _("Filter by endpoint name")
            connection_type = _("Filter by endpoint connection type")
            payload_type = _("Filter by endpoint payload type")
            status = _("Filter by endpoint status")

        class practitioner_role:
            active = _("Filter by active status")
            role = _("Filter by provider role code")
            specialty = _("Filter by Nucc/Snomed specialty code")

        class address:
            full = _("Filter by any part of address. Address filter accepts websearch syntax.")
            city = _("Filter by city name")
            state = _("Filter by state (2-letter abbreviation)")
            postalcode = _("Filter by postal code/zip code")
            use = _("Filter by address use type")

    class endpoints:
        # Descriptions for API endpoints

        class practitioner:
            viewset = _("ViewSet for FHIR Practitioner resources")
            list_description = _(
                "Query a list of healthcare providers, represented as a "
                "bundle of FHIR Practitioner resources"
            )
            default_sort = _("ascending last name, first name")
            retrieve_description = _("Query a specific provider as a FHIR Practitioner resource")
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of FHIR Practitioner resources"
            )
            retrieve_response = _("Successfully retrieved FHIR Practitioner resource")

        class practitioner_role:
            viewset = _("ViewSet for FHIR PractitionerRole resources")
            list_description = _(
                "Query a list of relationships between providers, healthcare "
                "organizations, and practice locations, represented as a "
                "bundle of FHIR PractitionerRole resources"
            )
            default_sort = _("ascending by location name")
            retrieve_description = _(
                "Query a specific relationship between providers, healthcare "
                "organizations, and practice locations, represented as a "
                "FHIR PractitionerRole resource"
            )
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of FHIR PractitionerRole resources"
            )
            retrieve_response = _("Successfully retrieved FHIR PractitionerRole resource")

        class organization:
            viewset = _("ViewSet for FHIR Organization resources")
            list_description = _(
                "Query a list of organizations, represented as a bundle "
                "of FHIR Organization resources"
            )
            default_sort = _("ascending by organization name")
            retrieve_description = _(
                "Query a specific organization, represented as a FHIR Organization resource"
            )
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of FHIR Organization resources"
            )
            retrieve_response = _("Successfully retrieved FHIR Organization resource")

        class organization_affiliation:
            viewset = _("ViewSet for FHIR EHR Vendor to Organization relationships")
            list_description = _(
                "Query a list of EHR vendor to organization relationships, "
                "represented as a bundle of FHIR OrganizationAffiliation "
                "resources"
            )
            default_sort = _("ascending by organization name")
            retrieve_description = _(
                "Query a specific EHR vendor to organization relationship, "
                "represented as a FHIR OrganizationAffiliation resource"
            )
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of "
                "FHIR OrganizationAffiliation resources"
            )
            retrieve_response = _("Successfully retrieved FHIR OrganizationAffiliation resource")

        class location:
            viewset = _("ViewSet for FHIR Location resources")
            list_description = _(
                "Query a list of healthcare practice locations, represented "
                "as a bundle of FHIR Location resources"
            )
            default_sort = _("ascending by location name")
            retrieve_description = _(
                "Query a specific healthcare practice location as a FHIR Location resource"
            )
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of FHIR Location resources"
            )
            retrieve_response = _("Successfully retrieved FHIR Location resource")

        class endpoint:
            viewset = _("ViewSet for FHIR Endpoint resources")
            list_description = _(
                "Query a list of interoperability endpoints, represented "
                "as a bundle of FHIR Endpoint resources"
            )
            default_sort = _("ascending by endpoint instance name")
            retrieve_description = _("Query a specific endpoint as a FHIR Endpoint resource")
            list_response = _(
                "Successfully retrieved FHIR Bundle resource of FHIR Endpoint resources"
            )
            retrieve_response = _("Successfully retrieved FHIR Endpoint resource")

        class capability_statement:
            viewset = _("ViewSet for FHIR CapabilityStatement resource")
            get_description = _(
                "Query metadata about this FHIR instance, represented as "
                "FHIR CapabilityStatement resource"
            )
            get_response = _("Successfully retrieved FHIR CapabilityStatement resource")
