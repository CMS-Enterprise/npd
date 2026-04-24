import type { Organization } from "../../src/@types/fhir/Organization"
import type { Practitioner } from "../../src/@types/fhir/Practitioner"
import type { FHIRCollection, FHIRPractitionerRole } from "../../src/@types/fhir"
import type { Location } from "../../src/@types/fhir/Location"
import type { Endpoint } from "../../src/@types/fhir/Endpoint"
import fhirOrganization from "./fhir_organization.json"
import fhirPractitioner from "./fhir_practitioner.json"
import fhirLocation1 from "./fhir_location_1.json"
import fhirLocation2 from "./fhir_location_2.json"
import fhirPractitionerRole from "./fhir_practitionerrole.json"
import fhirEndpoint from "./fhir_endpoint.json"
import fhirEmptyBundle from "./empty_bundle.json"
import fhirPractitionerRoleNoEndpoints from "./fhir_practitionerrole_noendpoints.json"
import fhirLocationsNoEndpoints from "./fhir_locations_noendpoints.json"
import fhirLocations from "./fhir_locations.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: Organization = fhirOrganization
export const DEFAULT_PRACTITIONER: Practitioner = fhirPractitioner
export const DEFAULT_PRACTITIONERROLE: FHIRCollection<FHIRPractitionerRole> = fhirPractitionerRole
export const DEFAULT_PRACTITIONERROLE_NOENDPOINTS: FHIRCollection<FHIRPractitionerRole> = fhirPractitionerRoleNoEndpoints
export const DEFAULT_LOCATION_1: Location = fhirLocation1
export const DEFAULT_LOCATION_2: Location = fhirLocation2
export const DEFAULT_LOCATIONS_NOENDPOINTS: FHIRCollection<Location> = fhirLocationsNoEndpoints
export const DEFAULT_LOCATIONS: FHIRCollection<Location> = fhirLocations
export const DEFAULT_ENDPOINT: Endpoint = fhirEndpoint
export const EMPTY_BUNDLE: FHIRCollection<never> = fhirEmptyBundle