import { useQueries, keepPreviousData, skipToken } from "@tanstack/react-query"
import type {
  FHIRCollection,
  FHIRPractitioner,
  FHIROrganization,
  FHIRPractitionerRole,
} from "../../@types/fhir"
import { defaultAdapter, type SearchAdapter } from "./searchAdapters"

export type SearchMode =
  | "providers"
  | "organizations"
  | "cross-entity"
  | "npi-lookup"
  | "none"

interface UseUnifiedSearchOptions {
  adapter?: SearchAdapter
}

export const getSearchMode = (params: UnifiedSearchParams): SearchMode => {
  const hasProviderFields = !!params.providerName
  const hasOrgFields = !!params.organizationName
  const hasNpi = !!params.npi

  if (hasProviderFields && hasOrgFields) return "cross-entity"
  if (hasProviderFields) return "providers"
  if (hasOrgFields) return "organizations"
  if (hasNpi) return "npi-lookup"
  return "none"
}

export const useUnifiedSearchAPI = (
  searchParams: UnifiedSearchParams,
  pagination: PaginationParams & { sort?: string },
  options?: UseUnifiedSearchOptions,
) => {
  const adapter = options?.adapter ?? defaultAdapter
  const searchMode = getSearchMode(searchParams)
  const hasSearch = searchMode !== "none"

  const results = useQueries({
    queries: [
      {
        queryKey: [
          "unified-practitioners",
          searchParams.providerName,
          searchParams.npi,
          searchParams.location,
          pagination.page || 1,
          pagination.sort,
        ],
        queryFn:
          searchMode === "providers" || searchMode === "npi-lookup"
            ? () => adapter.searchProviders(searchParams, pagination)
            : skipToken,
        placeholderData: keepPreviousData,
      },
      {
        queryKey: [
          "unified-organizations",
          searchParams.organizationName,
          searchParams.npi,
          searchParams.location,
          pagination.page || 1,
          pagination.sort,
        ],
        queryFn:
          searchMode === "organizations" || searchMode === "npi-lookup"
            ? () => adapter.searchOrganizations(searchParams, pagination)
            : skipToken,
        placeholderData: keepPreviousData,
      },
      {
        queryKey: [
          "unified-cross-entity",
          searchParams.providerName,
          searchParams.organizationName,
          searchParams.npi,
          searchParams.location,
          pagination.page || 1,
          pagination.sort,
        ],
        queryFn:
          searchMode === "cross-entity"
            ? () => adapter.searchCrossEntity(searchParams, pagination)
            : skipToken,
        placeholderData: keepPreviousData,
      },
    ],
  })

  const [practitionerQuery, organizationQuery, crossEntityQuery] = results

  return {
    practitioners: practitionerQuery.data as
      | FHIRCollection<FHIRPractitioner>
      | undefined,
    organizations: organizationQuery.data as
      | FHIRCollection<FHIROrganization>
      | undefined,
    practitionerRoles: crossEntityQuery.data as
      | FHIRCollection<FHIRPractitionerRole>
      | undefined,
    searchMode,
    isLoading:
      practitionerQuery.isLoading ||
      organizationQuery.isLoading ||
      crossEntityQuery.isLoading,
    isPlaceholderData:
      (practitionerQuery.isPlaceholderData ?? false) ||
      (organizationQuery.isPlaceholderData ?? false) ||
      (crossEntityQuery.isPlaceholderData ?? false),
    error:
      practitionerQuery.error ||
      organizationQuery.error ||
      crossEntityQuery.error,
    hasSearch,
  }
}
