import { Alert, Button, Pagination, Dropdown, type DropdownChangeObject  } from "@cmsgov/design-system"
import classNames from "classnames"
import React, { type ChangeEvent, type FormEvent, useState } from "react"
import { useTranslation } from "react-i18next"
import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import { PaginationCaption } from "../../components/PaginationCaption"
import { TitlePanel } from "../../components/TitlePanel"
import { apiUrl } from "../../state/api"
import { SearchProvider } from "../../state/Search/SearchProvider"
import { useSearchDispatch, useSearchState } from "../../state/Search/useSearch"
import layout from "../Layout.module.css"
import search from "../Search.module.css"
import { ListedPractitioner } from "./ListedPractitioner"
import { PRACTITIONER_SORT_OPTIONS, type PractitionerSortKey } from "../../state/requests/practitioners"
import { usePractitionersAPI } from "../../state/requests/practitioners"
import type { FHIRPractitioner } from "../../@types/fhir"
import { FaUserMd } from "react-icons/fa"

const PractitionerSearchForm: React.FC = () => {
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
    sort
  } = useSearchState<FHIRPractitioner>()

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

  const handleSort = (change: DropdownChangeObject): void => {
    const value = change.target.value
    setSort(value)
  }

  const sortOptions = Object.entries(PRACTITIONER_SORT_OPTIONS).map(
    ([value, option]) => ({
      value: value as PractitionerSortKey,
      label: t(option.labelKey),
    })
  )

  return (
    <>
      <TitlePanel
        icon={<FaUserMd size={42} aria-hidden="true" />}
        title={t("practitioners.search.title")}
        color="var(--color-primary-darkest)"
        className={layout.compactLeader}
      >
        <div className="ds-l-row">
          <div className="ds-l-col--12 ds-u-padding-bottom--4">
            <form onSubmit={handleSubmit}>
              <input type="hidden" name="page" value={pagination?.page} />
              <div className="ds-u-clearfix">
                <label className="ds-c-label" htmlFor="query">
                  {t("practitioners.search.inputLabel")}
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
                    disabled={query.length < 1 || isLoading && !isBackgroundLoading}
                  >
                    {isLoading && !isBackgroundLoading ? "Searching..." : "Search practitioners"}
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
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', gap: '8px' }}>
                      <PaginationCaption pagination={pagination} />
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: "8px" }}>
                      {t("practitioners.sort.by")}
                      <Dropdown
                        label=""
                        name="sort-dropdown-field"
                        labelClassName="ds-u-display--none"
                        options={sortOptions}
                        value={sort}
                        onChange={handleSort}
                      />
                    </div>
                  </div>
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
                        return apiUrl(`/practitioners?${nextParams.toString()}`)
                      }}
                      totalPages={pagination.totalPages}
                    />
                  </>
                )}
                <div data-testid="searchresults" role="list">
                  {data.map((practitioner) => (
                    <ListedPractitioner data={practitioner} key={practitioner.id} />
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
