import { skipToken, useQuery, keepPreviousData, useQueries } from "@tanstack/react-query"
import type { FHIRCollection, FHIROrganization, FHIRPractitionerRole, FHIRLocation, FHIREndpoint } from "../../@types/fhir"
import { apiUrl } from "../api"
import type { SortOption, SearchParams } from "../../@types/search"
import { fetchPractitionerRoles } from "./practitionerrole"
import { fetchLocations } from "./locations"
import { fetchEndpoint } from "./endpoints"

export const ORGANIZATION_SORT_OPTIONS: Record<string, SortOption> = {
  "name-asc": {
    labelKey: "organizations.sort.name-asc",
    apiValue: "name",
  },
  "name-desc": {
    labelKey: "organizations.sort.name-desc",
    apiValue: "-name",
  },
} as const

export type OrganizationSortKey = keyof typeof ORGANIZATION_SORT_OPTIONS

export interface OrganizationDetailsType extends FHIROrganization {
      practitionerRoleData: FHIRCollection<FHIRPractitionerRole> | undefined,
      practitionerData: Array<{id: string, name: string | undefined | null}>,
      locationData: FHIRCollection<FHIRLocation> | undefined,
      endpointData: Array<FHIREndpoint | undefined>,
  }

export const fetchOrganization = async (
  organizationId: string ,
  signal: AbortSignal | null | undefined
): Promise<FHIROrganization> => {
  const url = apiUrl("/fhir/Organization/:organizationId/", { organizationId })

  const response = await fetch(url, {signal})

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIROrganization>
}

export const useOrganizationAPI = (organizationId: string | undefined) => {
  return useQuery<FHIROrganization>({
    queryKey: ["organization", organizationId],
    queryFn: ({ signal }) => {
      if (!organizationId) {
        return Promise.reject("no organizationId was provided")
      }

      return fetchOrganization(organizationId, signal)
    },
  })
}

export const useFullOrganizationAPI = (organizationId: string | undefined) => {
  const {data: organization, isLoading: organizationLoading, error: organizationError} = useQuery<FHIROrganization>({
    queryKey: ["organization", organizationId],
    queryFn: ({ signal }) => {
      if (!organizationId) {
        return Promise.reject("no organizationId was provided")
      }

      return fetchOrganization(organizationId, signal)
    },
  })
  const npi = organization?.identifier?.filter(identifier => identifier.system = "http://terminology.hl7.org/NamingSystem/npi")[0].value?.toString();
  const {data: practitionerRole, isLoading: practitionerRoleLoading, error: practitionerRoleError} = useQuery<FHIRCollection<FHIRPractitionerRole>>({
    queryKey: ["practitionerRole", npi, organizationId],
    queryFn: ({ signal }) => fetchPractitionerRoles({organizationNPI: npi, signal: signal}),
    enabled: !!npi,
  })
  const {data: locations, isLoading: locationsLoading, error: locationsError} = useQuery<FHIRCollection<FHIRLocation>>({
    queryKey: ["locations", npi, organizationId],
    queryFn: ({ signal }) => fetchLocations(npi, signal),
    enabled: !!npi,
  })
  const practitionerDataDups = practitionerRole?.results.entry.map((role) => { 
    return {
    id: role?.resource.practitioner.reference.split('/').pop() ?? "", 
    name: role?.resource.practitioner.display
  }});
  const practitionerData = [...new Set(practitionerDataDups)];

  const endpointIdDups: Array<string | undefined> | undefined = locations?.results.entry.flatMap((location) => {return location?.resource.endpoint?.map(endpoint => endpoint.reference.split('/').pop() ?? "") }) ?? undefined;
    const endpointIds: Array<string | undefined> = [...new Set(endpointIdDups)];
    const endpointQueries = useQueries({
      queries: endpointIds.map((endpointId: string | undefined) => {
        return {
          queryKey: ["endpoint", npi, endpointId],
          queryFn: ({ signal }: {signal?: AbortSignal}) => { 
            if (endpointId !== undefined) {
              return fetchEndpoint(endpointId, signal)
            }
            else {
              return undefined
            }
          },
          enabled: !!location && !!endpointIds && !!endpointId,
        }
      }),
      combine: (results) => {
        return {
          data: results.map(result => result.data),
          loading: results.some((result) => result.isLoading) 
        }
      }
    })
  return {
    fullData: {
      ...organization,
      practitionerRoleData: practitionerRole,
      practitionerData: practitionerData,
      locationData: locations,
      endpointData: endpointQueries.data,
    },
    fullDataError: organizationError ?? practitionerRoleError ?? locationsError,
    fullDataLoading: organizationLoading || practitionerRoleLoading || locationsLoading || endpointQueries.loading,
    endpointDataLoading: practitionerRoleLoading || endpointQueries.loading,
    locationDataLoading: practitionerRoleLoading || locationsLoading,
    practitionerDataLoading: practitionerRoleLoading,
  }
}

const detectQueryKey = (value: string): "identifier" | "name" => {
  return /^\d+$/.test(value) ? "identifier" : "name"
}

const detectSortKey = (value: OrganizationSortKey): string => {
  return ORGANIZATION_SORT_OPTIONS[value]?.apiValue
}

/// list

export const fetchOrganizations = async (
  params: PaginationParams & SearchParams,
  signal: AbortSignal | null | undefined
): Promise<FHIRCollection<FHIROrganization>> => {
  const url = new URL(apiUrl("/fhir/Organization/"))

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
    if (key === "identifier") {
      url.searchParams.set(key, `NPI|${query}`)
    } else {
      url.searchParams.set(key, query)
    }
  }

  // Sort
  if (params.sort) {
    const apiValue = detectSortKey(params.sort as OrganizationSortKey)
    if (apiValue) {
      url.searchParams.set("_sort", apiValue)
    }
  }

  const response = await fetch(url, { signal })
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

export const useOrganizationsAPI = (
  params: PaginationParams & SearchParams, 
  options?: QueryOptions,
) => {
  return useQuery<FHIRCollection<FHIROrganization>>({
    queryKey: ["organizations", params.sort, params.query, params.page || 1],
    queryFn:
      options?.requireQuery && (!params.query || params.query.length === 0)
        ? skipToken
        : ({ signal }) => {
            return fetchOrganizations(params, signal)
          },
    placeholderData: keepPreviousData,
  })
}
