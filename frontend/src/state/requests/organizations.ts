import { skipToken, useQuery, keepPreviousData } from "@tanstack/react-query"
import type { FHIRCollection, FHIROrganization } from "../../@types/fhir"
import { formatAddress, formatDate } from "../../helpers/formatters"
import { apiUrl } from "../api"
import type { SortOption } from "../../@types/search"

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

const fetchOrganization = async (
  organizationId: string,
): Promise<FHIROrganization> => {
  const url = apiUrl("/fhir/Organization/:organizationId/", { organizationId })

  const response = await fetch(url)

  if (!response.ok) {
    console.error(await response.text())
    return Promise.reject(`error in ${url} request`)
  }

  return response.json() as Promise<FHIROrganization>
}

export const useOrganizationAPI = (organizationId: string | undefined) => {
  return useQuery<FHIROrganization>({
    queryKey: ["organization", organizationId],
    queryFn: () => {
      if (!organizationId) {
        return Promise.reject("no organizationId was provided")
      }

      return fetchOrganization(organizationId)
    },
  })
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

export const useOrganizationsAPI = (
  params: PaginationParams & SearchParams,
  options?: QueryOptions,
) => {
  return useQuery<FHIRCollection<FHIROrganization>>({
    queryKey: ["organizations", params.sort, params.query, params.page || 1],
    queryFn:
      options?.requireQuery && (!params.query || params.query.length === 0)
        ? skipToken
        : () => {
            return fetchOrganizations(params)
          },
    placeholderData: keepPreviousData,
  })
}

////
// Selectors unpack the API responses
////

export const organizationNpiSelector = (
  org?: Pick<FHIROrganization, "identifier">,
) => {
  if (!org) return ""

  if (!org.identifier?.length) {
    return "n/a"
  }

  const npiIdentifier = org.identifier.find(
    (ident) =>
      ident.system === "http://terminology.hl7.org/NamingSystem/npi" ||
      ident.system === "http://hl7.org/fhir/sid/us-npi",
  )

  return npiIdentifier?.value || "n/a"
}

export const organizationMailingAddressSelector = (org?: FHIROrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.address) return ""

  return formatAddress(contact.address)
}

export const organizationAuthorizedOfficialSelector = (
  org?: FHIROrganization,
) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  if (!contact.name) return ""

  return contact.name.text
}

export const organizationAuthorizedPhoneSelector = (org?: FHIROrganization) => {
  if (!org || !org.contact?.length) return ""

  const contact = org.contact[0]
  const phone = contact?.telecom?.find((t) => t.system === "phone")

  return phone?.value || ""
}

export const organizationIdentifiersSelector = (org?: FHIROrganization) => {
  if (!org || !org.identifier?.length) return []

  return org.identifier.map((identity) => ({
    type: identity.type?.coding?.[0]?.display || "Unknown",
    number: identity.value,
    details: identity.period?.start
      ? `Active, Received ${formatDate(identity.period.start)}` // hardcoding active and received if we get a response?
      : "",
    system: identity.system,
  }))
}
