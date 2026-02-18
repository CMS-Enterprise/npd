import { skipToken, useQuery } from "@tanstack/react-query"
import type { FHIRCollection, FHIRPractitioner } from "../../@types/fhir"
import { apiUrl } from "../api"
import type { SortOption } from "../../@types/search"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically

export const PRACTITIONER_SORT_OPTIONS: Record<string, SortOption> = {
  "first-name-asc": {
    labelKey: "practitioners.sort.first-asc",
    apiValue: "first_name",
  },
  "first-name-desc": {
    labelKey: "practitioners.sort.first-desc",
    apiValue: "-first_name",
  },
  "last-name-asc": {
    labelKey: "practitioners.sort.last-asc",
    apiValue: "last_name",
  },
  "last-name-desc": {
    labelKey: "practitioners.sort.last-desc",
    apiValue: "-last_name",
  },
} as const

export type PractitionerSortKey = keyof typeof PRACTITIONER_SORT_OPTIONS

const fetchPractitioner = async (
  practitionerId: string,
): Promise<FHIRPractitioner> => {
  const url = apiUrl("/fhir/Practitioner/:practitionerId/", { practitionerId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRPractitioner>
}

export const usePractitionerAPI = (practitionerId: string | undefined) => {
  return useQuery<FHIRPractitioner>({
    queryKey: ["practitioner", practitionerId],
    queryFn: () => {
      if (!practitionerId) {
        return Promise.reject("no practitionerId was provided")
      }

      return fetchPractitioner(practitionerId)
    },
  })
}

const detectQueryKey = (value: string): "identifier" | "name" => {
  return /^\d+$/.test(value) ? "identifier" : "name"
}

const detectSortKey = (value: PractitionerSortKey): string => {
  return PRACTITIONER_SORT_OPTIONS[value]?.apiValue
}

/// list

export const fetchPractitioners = async (
  params: PaginationParams & SearchParams,
): Promise<FHIRCollection<FHIRPractitioner>> => {
  const url = new URL(apiUrl("/fhir/Practitioner/"))

  // Pagination
  if (params.page) {
    url.searchParams.set("page", params.page.toString())
  }
  if (params.page_size) {
    url.searchParams.set("page_size", params.page_size.toString())
  }

  // Search
  if (params.query) {
    const query = params.query
    const key = detectQueryKey(query)
    url.searchParams.set(key, query)
  }

  // Sort
  if (params.sort) {
    const apiValue = detectSortKey(params.sort as PractitionerSortKey)
    if (apiValue) {
      url.searchParams.set("_sort", apiValue)
    }
  }

  const response = await fetch(url)
  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json()
}

type QueryOptions = {
  enabled?: boolean
  requireQuery?: boolean
}

export const usePractitionersAPI = (
  params: PaginationParams & SearchParams,
  options?: QueryOptions,
) => {
  return useQuery<FHIRCollection<FHIRPractitioner>>({
    queryKey: ["practitioners", params.sort, params.query, params.page || 1],
    queryFn:
      options?.requireQuery && (!params.query || params.query.length === 0)
        ? skipToken
        : () => {
            return fetchPractitioners(params)
          },
  })
}
