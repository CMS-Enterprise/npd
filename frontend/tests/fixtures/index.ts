import type { Organization } from "../../src/@types/fhir/Organization"
import type { Practitioner } from "../../src/@types/fhir/Practitioner"
import type { FHIRCollection, FHIRPractitionerRole } from "../../src/@types/fhir"
import type { Location } from "../../src/@types/fhir/Location"
import fhirOrganization from "./fhir_organization.json"
import fhirPractitioner from "./fhir_practitioner.json"
import fhirLocation from "./fhir_location.json"
import fhirPractitionerRole from "./fhir_practitionerrole.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: Organization = fhirOrganization
export const DEFAULT_PRACTITIONER: Practitioner = fhirPractitioner
export const DEFAULT_PRACTITIONERROLE: FHIRCollection<FHIRPractitionerRole> = fhirPractitionerRole
export const DEFAULT_LOCATION: Location = fhirLocation
