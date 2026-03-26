import { type FHIRLocation, type FHIRCollection } from "../../@types/fhir"
import { apiUrl } from "../api"

export const fetchLocation = async (
  locationId: string,
  signal: AbortSignal | null | undefined
): Promise<FHIRLocation> => {
  const url = apiUrl("/fhir/Location/:locationId/", { locationId })

  const response = await fetch(url, {signal})

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRLocation>
}

export const fetchLocations = async (
  organizationNPI: string | undefined,
  signal: AbortSignal | null | undefined
): Promise<FHIRCollection<FHIRLocation>> => {
  const url = apiUrl(`/fhir/Location/?page_size=1000&organization_identifier=NPI|${organizationNPI}`)

  const response = await fetch(url, {signal})

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRCollection<FHIRLocation>>
}