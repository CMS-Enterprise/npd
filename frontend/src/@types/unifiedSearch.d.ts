interface UnifiedSearchParams {
  providerName?: string
  npi?: string
  location?: string
  organizationName?: string
}

interface UnifiedSearchURLParams extends PaginationParams {
  provider_name?: string
  npi?: string
  location?: string
  organization_name?: string
  sort?: string
}
