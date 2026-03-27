import { type FHIREndpoint } from "../../@types/fhir"
import { apiUrl } from "../api"

export const fetchEndpoint = async (
  endpointId: string,
  signal: AbortSignal | null | undefined
): Promise<FHIREndpoint> => {
  const url = apiUrl("/fhir/Endpoint/:endpointId/", { endpointId })

  const response = await fetch(url, {signal})

  if (!response.ok) {
    console.error(`Endpoint error: ${await response.text()}`)
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIREndpoint>
}

export type EndpointQueryResultType = {
  data: FHIREndpoint | undefined,
  error: Error | null,
  status: 'loading' | 'error' | 'success' | 'pending'
}