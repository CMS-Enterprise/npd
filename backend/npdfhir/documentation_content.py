class docs:
    # Centralized namespace for all NPD API documentation content.

    class filters:
        # Help text for filter parameters, organized by FHIR resource

        class practitioner:
            name = (
                "Filter by practitioner name (first, middle, last, or full name). "
                "Name filter accepts websearch syntax."
            )
            gender = "Filter by practitioner gender"
            identifier = (
                "Filter by practitioner identifier (NPI or other). Format: value or system|value"
            )
            type = (
                "Filter by practitioner type/taxonomy. "
                "Practitioner type filter accepts websearch syntax."
            )

        class organization:
            name = "Filter by organization name"
            identifier = (
                "Filter by organization identifier (NPI, EIN, or other). "
                "Format: value or system|value"
            )
            type = "Filter by organization type/taxonomy"

        class location:
            name = "Filter by location name"
            near = (
                "Filter by distance from a point expressed as "
                "[latitude]|[longitude]|[distance]|[units]. "
                "If no units are provided, km is assumed."
            )

        class endpoint:
            name = "Filter by endpoint name"
            connection_type = "Filter by endpoint connection type"
            payload_type = "Filter by endpoint payload type"
            status = "Filter by endpoint status"

        class practitioner_role:
            active = "Filter by active status"
            role = "Filter by provider role code"
            specialty = "Filter by Nucc/Snomed specialty code"

        class address:
            full = "Filter by any part of address. Address filter accepts websearch syntax."
            city = "Filter by city name"
            state = "Filter by state (2-letter abbreviation)"
            postalcode = "Filter by postal code/zip code"
            use = "Filter by address use type"

    class endpoints:
        # Descriptions for API endpoints

        class practitioner:
            viewset = "ViewSet for FHIR Practitioner resources"
            list_description = (
                "Query a list of healthcare providers, represented as a "
                "bundle of FHIR Practitioner resources"
            )
            default_sort = "ascending last name, first name"
            retrieve_description = "Query a specific provider as a FHIR Practitioner resource"
            list_response = (
                "Successfully retrieved FHIR Bundle resource of FHIR Practitioner resources"
            )
            retrieve_response = "Successfully retrieved FHIR Practitioner resource"

        class practitioner_role:
            viewset = "ViewSet for FHIR PractitionerRole resources"
            list_description = (
                "Query a list of relationships between providers, healthcare "
                "organizations, and practice locations, represented as a "
                "bundle of FHIR PractitionerRole resources"
            )
            default_sort = "ascending by location name"
            retrieve_description = (
                "Query a specific relationship between providers, healthcare "
                "organizations, and practice locations, represented as a "
                "FHIR PractitionerRole resource"
            )
            list_response = (
                "Successfully retrieved FHIR Bundle resource of FHIR PractitionerRole resources"
            )
            retrieve_response = "Successfully retrieved FHIR PractitionerRole resource"

        class organization:
            viewset = "ViewSet for FHIR Organization resources"
            list_description = (
                "Query a list of organizations, represented as a bundle "
                "of FHIR Organization resources"
            )
            default_sort = "ascending by organization name"
            retrieve_description = (
                "Query a specific organization, represented as a FHIR Organization resource"
            )
            list_response = (
                "Successfully retrieved FHIR Bundle resource of FHIR Organization resources"
            )
            retrieve_response = "Successfully retrieved FHIR Organization resource"

        class organization_affiliation:
            viewset = "ViewSet for FHIR EHR Vendor to Organization relationships"
            list_description = (
                "Query a list of EHR vendor to organization relationships, "
                "represented as a bundle of FHIR OrganizationAffiliation "
                "resources"
            )
            default_sort = "ascending by organization name"
            retrieve_description = (
                "Query a specific EHR vendor to organization relationship, "
                "represented as a FHIR OrganizationAffiliation resource"
            )
            list_response = (
                "Successfully retrieved FHIR Bundle resource of "
                "FHIR OrganizationAffiliation resources"
            )
            retrieve_response = "Successfully retrieved FHIR OrganizationAffiliation resource"

        class location:
            viewset = "ViewSet for FHIR Location resources"
            list_description = (
                "Query a list of healthcare practice locations, represented "
                "as a bundle of FHIR Location resources"
            )
            default_sort = "ascending by location name"
            retrieve_description = (
                "Query a specific healthcare practice location as a FHIR Location resource"
            )
            list_response = "Successfully retrieved FHIR Bundle resource of FHIR Location resources"
            retrieve_response = "Successfully retrieved FHIR Location resource"

        class endpoint:
            viewset = "ViewSet for FHIR Endpoint resources"
            list_description = (
                "Query a list of interoperability endpoints, represented "
                "as a bundle of FHIR Endpoint resources"
            )
            default_sort = "ascending by endpoint instance name"
            retrieve_description = "Query a specific endpoint as a FHIR Endpoint resource"
            list_response = "Successfully retrieved FHIR Bundle resource of FHIR Endpoint resources"
            retrieve_response = "Successfully retrieved FHIR Endpoint resource"

        class capability_statement:
            viewset = "ViewSet for FHIR CapabilityStatement resource"
            get_description = (
                "Query metadata about this FHIR instance, represented as "
                "FHIR CapabilityStatement resource"
            )
            get_response = "Successfully retrieved FHIR CapabilityStatement resource"
