import { Alert, Button, Pagination } from "@cmsgov/design-system"
import classNames from "classnames"
import React, { type ChangeEvent, type FormEvent, useState } from "react"
import { useTranslation } from "react-i18next"
import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { TitlePanel } from "../../components/TitlePanel"
import { apiUrl } from "../../state/api"
import { SearchProvider } from "../../state/Search/SearchProvider"
import { useSearchDispatch, useSearchState } from "../../state/Search/useSearch"
import layout from "../Layout.module.css"
import search from "../Search.module.css"
import { ListedOrganization } from "./ListedOrganization"
import {
  ORGANIZATION_SORT_OPTIONS,
  type OrganizationSortKey,
} from "../../state/requests/organizations"
import { useOrganizationsAPI } from "../../state/requests/organizations"
import type { FHIROrganization } from "../../@types/fhir"
import { FaHospital } from "react-icons/fa"
import { SearchResultsHeader } from "../../components/SearchResultsHeader"

const OrganizationSearchForm: React.FC = () => {
  const { t } = useTranslation()
  const { setQuery, navigateToPage, setSort } = useSearchDispatch()
  const {
    isLoading,
    isBackgroundLoading,
    initialQuery,
    query: searchQuery,
    error: searchError,
    data,
    pagination,
    sort,
  } = useSearchState<FHIROrganization>()

  const [query, setQueryValue] = useState<string>(initialQuery || "")

  const contentClass = classNames(layout.content, "ds-l-container")
  const inputClass = classNames(search.input)

  const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    setQuery(query)
  }

  const handleInputChange = (e: ChangeEvent<HTMLInputElement>): void => {
    const value = e.target.value
    setQueryValue(value)
  }

  const sortOptions = Object.entries(ORGANIZATION_SORT_OPTIONS).map(
    ([value, option]) => ({
      value: value as OrganizationSortKey,
      label: t(option.labelKey),
    }),
  )

  return (
    <>
      <TitlePanel
        icon={<FaHospital size={42} aria-hidden="true" />}
        title={t("organizations.search.title")}
        color="var(--color-primary-darkest)"
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-padding-bottom--4">
            <form onSubmit={handleSubmit}>
              <input type="hidden" name="page" value={pagination?.page} />
              <div className="ds-u-clearfix">
                <label className="ds-c-label" htmlFor="query">
                  {t("organizations.search.inputLabel")}
                </label>
                <div className={inputClass}>
                  <input
                    className="ds-c-field"
                    type="text"
                    name="query"
                    id="query"
                    value={query}
                    onChange={handleInputChange}
                  />
                  <Button
                    type="submit"
                    variation="solid"
                    disabled={
                      query.length < 1 || (isLoading && !isBackgroundLoading)
                    }
                  >
                    {isLoading && !isBackgroundLoading
                      ? "Searching..."
                      : "Search"}
                  </Button>
                </div>
              </div>
            </form>
          </div>
        </div>
      </TitlePanel>

      <main className={contentClass}>
        <div className="ds-l-row">
          {searchError && (
            <div className="error-message">
              <strong>Error:</strong> {searchError}
            </div>
          )}

          <div className="ds-l-col--12 ds-u-margin-bottom--7">
            {data && data.length > 0 && (
              <>
                {pagination && (
                  <>
                    <SearchResultsHeader
                      pagination={pagination}
                      options={sortOptions}
                      value={sort}
                      onChange={setSort}
                      inputLabel={"organizations.sort.by"}
                    />
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
                        return apiUrl(`/organizations?${nextParams.toString()}`)
                      }}
                      totalPages={pagination.totalPages}
                    />
                  </>
                )}
                <div data-testid="searchresults" role="list">
                  {data.map((org) => (
                    <ListedOrganization data={org} key={org.id} />
                  ))}
                </div>
              </>
            )}

            {data && data.length === 0 && (
              <p>No Organizations found for query: {query}</p>
            )}

            {!data && (
              <Alert heading={t("organizations.alert.heading")}>
                <NpdMarkdown content={t("organizations.alert.body")} />
              </Alert>
            )}
          </div>
        </div>
      </main>
    </>
  )
}

export const OrganizationSearch = () => {
  return (
    <SearchProvider useSearchAPI={useOrganizationsAPI} defaultSort="name-asc">
      <OrganizationSearchForm />
    </SearchProvider>
  )
}
