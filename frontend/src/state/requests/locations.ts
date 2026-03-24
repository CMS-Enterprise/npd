import { type FHIRLocation, type FHIRCollection } from "../../@types/fhir"
import { apiUrl } from "../api"

export const fetchLocation = async (
  locationId: string,
): Promise<FHIRLocation> => {
  const url = apiUrl("/fhir/Location/:locationId/", { locationId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRLocation>
}

export const fetchLocations = async (
  organizationNPI: string | undefined,
): Promise<FHIRCollection<FHIRLocation>> => {
  const url = apiUrl(`/fhir/Location?organization_identifier=NPI|${organizationNPI}`)

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRCollection<FHIRLocation>>
}