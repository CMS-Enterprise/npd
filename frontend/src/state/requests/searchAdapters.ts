import type {
  FHIRCollection,
  FHIRPractitioner,
  FHIROrganization,
  FHIRPractitionerRole,
} from "../../@types/fhir"
import { apiUrl } from "../api"

export interface SearchAdapter {
  searchProviders(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIRPractitioner>>

  searchOrganizations(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIROrganization>>

  searchCrossEntity(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIRPractitionerRole>>
}

const parseLocationParam = (location: string, url: URL, prefix = "") => {
  const trimmed = location.trim()
  if (/^\d{5}$/.test(trimmed)) {
    url.searchParams.set(`${prefix}address_postalcode`, trimmed)
  } else if (/^[A-Za-z]{2}$/.test(trimmed)) {
    url.searchParams.set(`${prefix}address_state`, trimmed.toUpperCase())
  } else {
    url.searchParams.set(`${prefix}address`, trimmed)
  }
}

export class FastAPISearchAdapter implements SearchAdapter {
  async searchProviders(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIRPractitioner>> {
    const url = new URL(apiUrl("/fhir/Practitioner/"))

    if (pagination.page) {
      url.searchParams.set("page", pagination.page.toString())
    }
    if (pagination.page_size) {
      url.searchParams.set("page_size", pagination.page_size.toString())
    }
    if (pagination.sort) {
      url.searchParams.set("_sort", pagination.sort)
    }

    if (params.providerName) {
      url.searchParams.set("name", params.providerName)
    }
    if (params.npi) {
      url.searchParams.set("identifier", params.npi)
    }
    if (params.location) {
      parseLocationParam(params.location, url)
    }

    const response = await fetch(url)
    if (!response.ok) {
      console.error(await response.text())
      return Promise.reject(`error in ${url} request`)
    }
    return response.json()
  }

  async searchOrganizations(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIROrganization>> {
    const url = new URL(apiUrl("/fhir/Organization/"))

    if (pagination.page) {
      url.searchParams.set("page", pagination.page.toString())
    }
    if (pagination.page_size) {
      url.searchParams.set("page_size", pagination.page_size.toString())
    }
    if (pagination.sort) {
      url.searchParams.set("_sort", pagination.sort)
    }

    if (params.organizationName) {
      url.searchParams.set("name", params.organizationName)
    }
    if (params.npi) {
      url.searchParams.set("identifier", `NPI|${params.npi}`)
    }
    if (params.location) {
      parseLocationParam(params.location, url)
    }

    const response = await fetch(url)
    if (!response.ok) {
      console.error(await response.text())
      return Promise.reject(`error in ${url} request`)
    }
    return response.json()
  }

  async searchCrossEntity(
    params: UnifiedSearchParams,
    pagination: PaginationParams & { sort?: string },
  ): Promise<FHIRCollection<FHIRPractitionerRole>> {
    const url = new URL(apiUrl("/fhir/PractitionerRole/"))

    if (pagination.page) {
      url.searchParams.set("page", pagination.page.toString())
    }
    if (pagination.page_size) {
      url.searchParams.set("page_size", pagination.page_size.toString())
    }
    if (pagination.sort) {
      url.searchParams.set("_sort", pagination.sort)
    }

    if (params.providerName) {
      url.searchParams.set("practitioner_name", params.providerName)
    }
    if (params.npi) {
      url.searchParams.set("practitioner_identifier", `NPI|${params.npi}`)
    }
    if (params.organizationName) {
      url.searchParams.set("organization_name", params.organizationName)
    }
    if (params.location) {
      parseLocationParam(params.location, url, "location_")
    }

    const response = await fetch(url)
    if (!response.ok) {
      console.error(await response.text())
      return Promise.reject(`error in ${url} request`)
    }
    return response.json()
  }
}

export const defaultAdapter = new FastAPISearchAdapter()
