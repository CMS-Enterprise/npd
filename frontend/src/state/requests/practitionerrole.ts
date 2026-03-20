import { type FHIRPractitionerRole, type FHIRCollection } from "../../@types/fhir"
import { apiUrl } from "../api"

export const fetchPractitionerRole = async (
  practitionerNPI?: string | undefined,
  organizationNPI?: string | undefined,
): Promise<FHIRPractitionerRole> => {
  var query: Array<string> = []
  if (practitionerNPI !== undefined) {
    query.push(`practitioner_identifier=NPI|${practitionerNPI}`);
  }
  if (organizationNPI !== undefined) {
    query.push(`organization_identifier=NPI|${organizationNPI}`);
  }
  const url = apiUrl(`/fhir/PractitionerRole/?${query.join('&')}`);

  const response = await fetch(url);

  if (!response.ok) {
    console.error(await response.text());
    return Promise.reject(`error in ${url} request`);
  }

  return response.json() as Promise<FHIRCollection<FHIRPractitionerRole>>
}