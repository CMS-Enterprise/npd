import { Alert, Pagination } from "@cmsgov/design-system"
import classNames from "classnames"
import React, { useState } from "react"
import { useTranslation } from "react-i18next"
import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { TitlePanel } from "../../components/TitlePanel"
import { apiUrl } from "../../state/api"
import { SearchProvider } from "../../state/Search/SearchProvider"
import { useSearchDispatch, useSearchState } from "../../state/Search/useSearch"
import layout from "../Layout.module.css"
import { ListedPractitioner } from "./ListedPractitioner"
import {
  PRACTITIONER_SORT_OPTIONS,
  type PractitionerSortKey,
} from "../../state/requests/practitioners"
import { usePractitionersAPI } from "../../state/requests/practitioners"
import type { FHIRPractitioner } from "../../@types/fhir"
import { FaUserMd } from "react-icons/fa"
import { SearchResultsHeader } from "../../components/SearchResultsHeader"
import { SearchBar } from "../../components/SearchBar"

const PractitionerSearchForm: React.FC = () => {
  const { t } = useTranslation()
  const { setQuery, navigateToPage, setSort } = useSearchDispatch()
  const {
    isLoading,
    isBackgroundLoading,
    isPlaceholderData,
    initialQuery,
    query: searchQuery,
    error: searchError,
    data,
    pagination,
    sort,
  } = useSearchState<FHIRPractitioner>()

  const [query, setQueryValue] = useState<string>(initialQuery || "")

  const contentClass = classNames(layout.content, "ds-l-container")

  const sortOptions = Object.entries(PRACTITIONER_SORT_OPTIONS).map(
    ([value, option]) => ({
      value: value as PractitionerSortKey,
      label: t(option.labelKey),
    }),
  )

  const hasResults = data && data.length > 0

  return (
    <>
      <TitlePanel
        icon={<FaUserMd size={42} aria-hidden="true" />}
        title={t("practitioners.search.title")}
        color="var(--color-primary-darkest)"
        className={layout.compactLeader}
      >
        <SearchBar
          value={query}
          onChange={setQueryValue}
          onSearch={setQuery}
          labelKey="practitioners.search.inputLabel"
          buttonTextKey="practitioners.search.button"
          isLoading={isLoading}
          isBackgroundLoading={isBackgroundLoading}
          isPlaceholderData={isPlaceholderData}
        />
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          {searchError && (
            <div className="error-message">
              <strong>Error:</strong> {searchError}
            </div>
          )}

          <div className="ds-l-col--12 ds-u-margin-bottom--7">
            {hasResults && (
              <>
                {pagination && (
                  <>
                    <SearchResultsHeader
                      pagination={pagination}
                      options={sortOptions}
                      value={sort}
                      onChange={setSort}
                      inputLabel={"practitioners.sort.by"}
                      disabled={isPlaceholderData}
                    />
                    <div
                      style={{
                        opacity: isPlaceholderData ? 0.5 : 1,
                        transition: "opacity 200ms ease",
                        pointerEvents: isPlaceholderData ? "none" : "auto",
                      }}
                    >
                      <Pagination
                        currentPage={pagination.page}
                        onPageChange={(evt, page) => {
                          evt.preventDefault()
                          evt.stopPropagation()
                          navigateToPage(page)
                        }}
                        renderHref={(pageNumber) => {
                          const nextParams = new URLSearchParams()
                          nextParams.set("page", pageNumber.toString())
                          if (searchQuery) nextParams.set("query", searchQuery)
                          return apiUrl(
                            `/practitioners?${nextParams.toString()}`,
                          )
                        }}
                        totalPages={pagination.totalPages}
                      />
                    </div>
                  </>
                )}
                <div
                  data-testid="searchresults"
                  role="list"
                  style={{
                    opacity: isPlaceholderData ? 0.5 : 1,
                    transition: "opacity 200ms ease",
                    pointerEvents: isPlaceholderData ? "none" : "auto",
                  }}
                >
                  {data.map((practitioner) => (
                    <ListedPractitioner
                      data={practitioner}
                      key={practitioner.id}
                    />
                  ))}
                </div>
              </>
            )}

            {data && data.length === 0 && (
              <p>No Practitioners found for query: {query}</p>
            )}

            {!data && (
              <Alert heading={t("practitioners.alert.heading")}>
                <NpdMarkdown content={t("practitioners.alert.body")} />
              </Alert>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export const PractitionerSearch = () => {
  return (
    <SearchProvider
      useSearchAPI={usePractitionersAPI}
      defaultSort="first-name-asc"
    >
      <PractitionerSearchForm />
    </SearchProvider>
  )
}
