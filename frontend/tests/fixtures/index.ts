import type { Organization } from "../../src/@types/fhir/Organization"
import type { Practitioner } from "../../src/@types/fhir/Practitioner"
import fhirOrganization from "./fhir_organization.json"
import fhirPractitioner from "./fhir_practitioner.json"

export const DEFAULT_FRONTEND_SETTINGS: FrontendSettings = {
  require_authentication: false,
  user: { is_anonymous: false, username: "testuser" },
  feature_flags: {},
}

export const DEFAULT_ORGANIZATION: Organization = fhirOrganization
export const DEFAULT_PRACTITIONER: Practitioner = fhirPractitioner
