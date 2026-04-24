import {
  skipToken,
  useQuery,
  keepPreviousData,
  useQueries,
} from "@tanstack/react-query"
import {
  type FHIRLocation,
  type FHIREndpoint,
  type FHIRPractitionerRole,
  type FHIRCollection,
  type FHIRPractitioner,
  type FHIROrganization,
} from "../../@types/fhir"
import { apiUrl } from "../api"
import { fetchOrganization } from "./organizations"
import { fetchEndpoint, type EndpointQueryResultType } from "./endpoints"
import { fetchLocation } from "./locations"
import { fetchPractitionerRoles } from "./practitionerrole"
import type { SortOption, SearchParams } from "../../@types/search"
import type { ContactPoint } from "../../@types/fhir/ContactPoint"

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

export type OrganizationDetails = {
  [key: string]: {
    organization: FHIROrganization
    endpoints: Array<
      | {
          id: string
          connectionType: string | undefined | null
          address: string | undefined | null
        }
      | undefined
    >
    locations: Array<{
      id: string
      name: string | undefined | null
      address: string
      contact?: Array<ContactPoint> | null | undefined
    }>
    roleDetails: FHIRPractitionerRole | undefined
  }
}

export interface PractitionerDetailsType extends FHIRPractitioner {
  practitionerRoleData: FHIRCollection<FHIRPractitionerRole> | undefined
  organizationData: { [key: string]: FHIROrganization }
  locationData: { [key: string]: FHIRLocation }
  endpointData: { [key: string]: FHIREndpoint }
}

export const fetchPractitioner = async (
  practitionerId: string,
  signal: AbortSignal | null | undefined,
): Promise<FHIRPractitioner> => {
  const url = apiUrl("/fhir/Practitioner/:practitionerId/", { practitionerId })

  const response = await fetch(url, { signal })

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIRPractitioner>
}

export const usePractitionerAPI = (practitionerId: string | undefined) => {
  return useQuery<FHIRPractitioner>({
    queryKey: ["practitioner", practitionerId],
    queryFn: ({ signal }) => {
      if (!practitionerId) {
        return Promise.reject("no practitionerId was provided")
      }

      return fetchPractitioner(practitionerId, signal)
    },
  })
}

export const useFullPractitionerAPI = (practitionerId: string | undefined) => {
  const {
    data: practitioner,
    isLoading: practitionerLoading,
    error: practitionerError,
  } = useQuery<FHIRPractitioner>({
    queryKey: ["practitioner", practitionerId],
    queryFn: ({ signal }) => {
      if (!practitionerId) {
        return Promise.reject("no practitionerId was provided")
      }

      return fetchPractitioner(practitionerId, signal)
    },
  })
  const npi = practitioner?.identifier
    ?.find(
      (identifier) =>
        identifier.system === "http://terminology.hl7.org/NamingSystem/npi" ||
        identifier.system === "http://hl7.org/fhir/sid/us-npi",
    )
    ?.value?.toString()
  const {
    data: practitionerRole,
    isLoading: practitionerRoleLoading,
    error: practitionerRoleError,
  } = useQuery<FHIRCollection<FHIRPractitionerRole>>({
    queryKey: ["practitionerRole", npi, practitionerId],
    queryFn: ({ signal }) =>
      fetchPractitionerRoles({ practitionerNPI: npi, signal: signal }),
    enabled: !!npi,
  })
  const organizationIdDups: Array<string> | undefined =
    practitionerRole?.results.entry.map((role) => {
      return role?.resource.organization.reference.split("/").pop() ?? ""
    })
  const organizationIds: Array<string> = [...new Set(organizationIdDups)]
  const organizationQueries = useQueries({
    queries: organizationIds.map((organizationId: string) => {
      return {
        queryKey: ["organization", npi, organizationId],
        queryFn: ({ signal }: { signal?: AbortSignal }) =>
          fetchOrganization(organizationId, signal),
        enabled: !!organizationIds,
      }
    }),
    combine: (results) => {
      return {
        data: Object.fromEntries(
          results.map((result) => [result.data?.id, result.data]),
        ),
        loading: results.some((result) => result.isLoading),
      }
    },
  })
  const locationIdDups: Array<string> | undefined =
    practitionerRole?.results.entry.flatMap((role) => {
      return (
        role?.resource.location.map(
          (locationReference) =>
            locationReference.reference.split("/").pop() ?? "",
        ) ?? []
      )
    })
  const locationIds: Array<string> = [...new Set(locationIdDups)]
  const locationQueries = useQueries({
    queries: locationIds.map((locationId: string) => {
      return {
        queryKey: ["location", npi, locationId],
        queryFn: ({ signal }: { signal?: AbortSignal }) =>
          fetchLocation(locationId, signal),
        enabled: !!locationIds,
      }
    }),
    combine: (results) => {
      return {
        data: Object.fromEntries(
          results.map((result) => [result.data?.id, result.data]),
        ),
        loading: results.some((result) => result.isLoading),
      }
    },
  })
  const endpointIdDups: Array<string | undefined> | undefined =
    practitionerRole?.results.entry.flatMap((role) => {
      return role?.resource.endpoint?.map(
        (endpoint) => endpoint.reference.split("/").pop() ?? "",
      )
    }) ?? undefined
  const endpointIds: Array<string | undefined> = [...new Set(endpointIdDups)]
  const endpointQueries = useQueries({
    queries: endpointIds.map((endpointId: string | undefined) => {
      return {
        queryKey: ["endpoint", npi, endpointId],
        queryFn: ({ signal }: { signal?: AbortSignal }) => {
          if (endpointId !== undefined) {
            return fetchEndpoint(endpointId, signal)
          } else {
            return undefined
          }
        },
        enabled: !!practitionerRole && !!endpointIds && !!endpointId,
      }
    }),
    combine: (results) => {
      return {
        data: Object.fromEntries(
          results.map((result: EndpointQueryResultType) => [
            result.data?.id,
            result.data,
          ]),
        ),
        loading: results.some((result) => result.isLoading),
      }
    },
  })
  return {
    fullData: {
      ...practitioner,
      practitionerRoleData: practitionerRole,
      organizationData: organizationQueries.data,
      locationData: locationQueries.data,
      endpointData: endpointQueries.data,
    },
    fullDataError: practitionerError ?? practitionerRoleError,
    fullDataLoading:
      practitionerLoading ||
      practitionerRoleLoading ||
      organizationQueries.loading ||
      endpointQueries.loading ||
      locationQueries.loading,
  }
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
    placeholderData: keepPreviousData,
  })
}
