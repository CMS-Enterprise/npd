import { type FHIRPractitionerRole, type FHIRCollection } from "../../@types/fhir"
import { apiUrl } from "../api"

interface PractitionerRoleParams {
    practitionerNPI?: string | undefined,
    organizationNPI?: string | undefined,
}

export const fetchPractitionerRoles = async (
  {practitionerNPI, organizationNPI}: PractitionerRoleParams
): Promise<FHIRCollection<FHIRPractitionerRole>> => {
  const query: Array<string> = []
  if (practitionerNPI !== undefined) {
    query.push(`practitioner_identifier=NPI|${practitionerNPI}`);
  }
  if (organizationNPI !== undefined) {
    query.push(`organization_identifier=NPI|${organizationNPI}`);
  }
  if (query.length > 0) {
    const url = apiUrl(`/fhir/PractitionerRole/?page_size=1000&${query.join('&')}`);

    const response = await fetch(url);

    if (!response.ok) {
      console.error(await response.text());
      return Promise.reject(`error in ${url} request`);
    }

    return response.json() as Promise<FHIRCollection<FHIRPractitionerRole>>
  }
  else {
    console.error('No query params provided');
    return Promise.reject(`No query params provided`);
  }
}