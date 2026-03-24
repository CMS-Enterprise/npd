import type { Organization } from "../../src/@types/fhir/Organization"
import type { Practitioner } from "../../src/@types/fhir/Practitioner"
import type { FHIRCollection, FHIRPractitionerRole } from "../../src/@types/fhir"
import type { Location } from "../../src/@types/fhir/Location"
import type { Endpoint } from "../../src/@types/fhir/Endpoint"
import fhirOrganization from "./fhir_organization.json"
import fhirPractitioner from "./fhir_practitioner.json"
import fhirLocation from "./fhir_location.json"
import fhirPractitionerRole from "./fhir_practitionerrole.json"
import fhirEndpoint from "./fhir_endpoint.json"
import fhirEmptyBundle from "./empty_bundle.json"
import fhirPractitionerRoleNoEndpoints from "./fhir_practitionerrole_noendpoints.json"
import fhirLocationNoEndpoints from "./fhir_location_noendpoints.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: Organization = fhirOrganization
export const DEFAULT_PRACTITIONER: Practitioner = fhirPractitioner
export const DEFAULT_PRACTITIONERROLE: FHIRCollection<FHIRPractitionerRole> = fhirPractitionerRole
export const DEFAULT_PRACTITIONERROLE_NOENDPOINTS: FHIRCollection<FHIRPractitionerRole> = fhirPractitionerRoleNoEndpoints
export const DEFAULT_LOCATION: Location = fhirLocation
export const DEFAULT_LOCATION_NOENDPOINTS: Location = fhirLocationNoEndpoints
export const DEFAULT_ENDPOINT: Endpoint = fhirEndpoint
export const EMPTY_BUNDLE: FHIRCollection<never> = fhirEmptyBundle