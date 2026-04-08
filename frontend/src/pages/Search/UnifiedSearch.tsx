import { useState } from "react"
import { useSearchParams } from "react-router"
import classNames from "classnames"
import { useTranslation } from "react-i18next"
import { FaSearch } from "react-icons/fa"
import { TitlePanel } from "../../components/TitlePanel"
import { UnifiedSearchForm } from "../../components/UnifiedSearchForm"
import { UnifiedSearchResults } from "./UnifiedSearchResults"
import { useUnifiedSearchAPI } from "../../state/requests/unifiedSearch"
import layout from "../Layout.module.css"

const readSearchParams = (search: URLSearchParams): UnifiedSearchParams => ({
  providerName: search.get("provider_name") || undefined,
  npi: search.get("npi") || undefined,
  location: search.get("location") || undefined,
  organizationName: search.get("organization_name") || undefined,
})

const toURLParams = (
  params: UnifiedSearchParams,
  page: number,
): Record<string, string> => {
  const out: Record<string, string> = {}
  if (params.providerName) out.provider_name = params.providerName
  if (params.npi) out.npi = params.npi
  if (params.location) out.location = params.location
  if (params.organizationName) out.organization_name = params.organizationName
  out.page = page.toString()
  return out
}

export const UnifiedSearch = () => {
  const { t } = useTranslation()
  const [searchParams, setSearchParams] = useSearchParams()
  const contentClass = classNames(layout.content, "ds-l-container")

  const committedParams = readSearchParams(searchParams)
  const currentPage = parseInt(searchParams.get("page") || "1", 10) || 1

  const [formValues, setFormValues] = useState<UnifiedSearchParams>({
    providerName: committedParams.providerName || "",
    npi: committedParams.npi || "",
    location: committedParams.location || "",
    organizationName: committedParams.organizationName || "",
  })

  const {
    practitioners,
    organizations,
    practitionerRoles,
    searchMode,
    isLoading,
    isPlaceholderData,
    error,
    hasSearch,
  } = useUnifiedSearchAPI(committedParams, { page: currentPage, page_size: 10 })

  const handleSearch = (values: UnifiedSearchParams) => {
    setSearchParams(toURLParams(values, 1), { preventScrollReset: true })
  }

  const handleClear = () => {
    setFormValues({
      providerName: "",
      npi: "",
      location: "",
      organizationName: "",
    })
    setSearchParams({})
  }

  const handlePageChange = (page: number) => {
    setSearchParams(toURLParams(committedParams, page), {
      preventScrollReset: true,
    })
  }

  return (
    <>
      <TitlePanel
        icon={<FaSearch size={42} aria-hidden="true" />}
        title={t("search.unified.title")}
        color="var(--color-primary-darkest)"
        className={layout.compactLeader}
      >
        <UnifiedSearchForm
          values={formValues}
          onChange={setFormValues}
          onSearch={handleSearch}
          onClear={handleClear}
          isLoading={isLoading}
        />
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-margin-bottom--7">
            <UnifiedSearchResults
              practitioners={practitioners}
              organizations={organizations}
              practitionerRoles={practitionerRoles}
              searchMode={searchMode}
              isLoading={isLoading}
              isPlaceholderData={isPlaceholderData}
              hasSearch={hasSearch}
              error={error}
              page={currentPage}
              onPageChange={handlePageChange}
            />
          </div>
        </div>
      </main>
    </>
  )
}
