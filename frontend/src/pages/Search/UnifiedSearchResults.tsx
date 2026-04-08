import { Alert, Pagination } from "@cmsgov/design-system"
import { useTranslation } from "react-i18next"
import type {
  FHIRCollection,
  FHIRPractitioner,
  FHIROrganization,
  FHIRPractitionerRole,
} from "../../@types/fhir"
import { ListedPractitioner } from "../Practitioner/ListedPractitioner"
import { ListedOrganization } from "../Organization/ListedOrganization"
import { NpdMarkdown } from "../../components/markdown/NpdMarkdown"
import type { SearchMode } from "../../state/requests/unifiedSearch"

type ResultItem =
  | { type: "provider"; data: FHIRPractitioner }
  | { type: "organization"; data: FHIROrganization }
  | { type: "role"; data: FHIRPractitionerRole }

type Props = {
  practitioners: FHIRCollection<FHIRPractitioner> | undefined
  organizations: FHIRCollection<FHIROrganization> | undefined
  practitionerRoles: FHIRCollection<FHIRPractitionerRole> | undefined
  searchMode: SearchMode
  isLoading: boolean
  isPlaceholderData: boolean
  hasSearch: boolean
  error: Error | null
  page: number
  onPageChange: (page: number) => void
}

const buildResultItems = (
  practitioners: FHIRCollection<FHIRPractitioner> | undefined,
  organizations: FHIRCollection<FHIROrganization> | undefined,
  practitionerRoles: FHIRCollection<FHIRPractitionerRole> | undefined,
  searchMode: SearchMode,
): ResultItem[] => {
  const items: ResultItem[] = []

  if (searchMode === "cross-entity" && practitionerRoles?.results?.entry) {
    for (const entry of practitionerRoles.results.entry) {
      if (entry?.resource) items.push({ type: "role", data: entry.resource })
    }
    return items
  }

  if (searchMode === "npi-lookup") {
    const hasPractitioner = (practitioners?.results?.entry?.length ?? 0) > 0
    const hasOrganization = (organizations?.results?.entry?.length ?? 0) > 0

    if (hasPractitioner && practitioners?.results?.entry) {
      for (const entry of practitioners.results.entry) {
        if (entry?.resource)
          items.push({ type: "provider", data: entry.resource })
      }
    } else if (hasOrganization && organizations?.results?.entry) {
      for (const entry of organizations.results.entry) {
        if (entry?.resource)
          items.push({ type: "organization", data: entry.resource })
      }
    }
    return items
  }

  if (practitioners?.results?.entry) {
    for (const entry of practitioners.results.entry) {
      if (entry?.resource)
        items.push({ type: "provider", data: entry.resource })
    }
  }
  if (organizations?.results?.entry) {
    for (const entry of organizations.results.entry) {
      if (entry?.resource)
        items.push({ type: "organization", data: entry.resource })
    }
  }
  return items
}

const getTotalCount = (
  practitioners: FHIRCollection<FHIRPractitioner> | undefined,
  organizations: FHIRCollection<FHIROrganization> | undefined,
  practitionerRoles: FHIRCollection<FHIRPractitionerRole> | undefined,
  searchMode: SearchMode,
): number => {
  if (searchMode === "cross-entity") return practitionerRoles?.count ?? 0
  if (searchMode === "npi-lookup") {
    const practCount = practitioners?.count ?? 0
    return practCount > 0 ? practCount : (organizations?.count ?? 0)
  }
  return (practitioners?.count ?? 0) + (organizations?.count ?? 0)
}

const getTotalPages = (
  practitioners: FHIRCollection<FHIRPractitioner> | undefined,
  organizations: FHIRCollection<FHIROrganization> | undefined,
  practitionerRoles: FHIRCollection<FHIRPractitionerRole> | undefined,
  searchMode: SearchMode,
  pageSize: number,
): number => {
  let maxCount: number
  if (searchMode === "cross-entity") {
    maxCount = practitionerRoles?.count ?? 0
  } else if (searchMode === "npi-lookup") {
    const practCount = practitioners?.count ?? 0
    maxCount = practCount > 0 ? practCount : (organizations?.count ?? 0)
  } else {
    maxCount = Math.max(practitioners?.count ?? 0, organizations?.count ?? 0)
  }
  return Math.max(1, Math.ceil(maxCount / pageSize))
}

const extractId = (reference?: string | null): string | null =>
  reference?.split("/").pop() ?? null

const getRoleTaxonomyDisplay = (
  role: FHIRPractitionerRole,
): string | undefined => {
  const first = role.specialty?.[0]
  if (!first) return undefined
  return first.text || first.coding?.[0]?.display || undefined
}

export const UnifiedSearchResults = ({
  practitioners,
  organizations,
  practitionerRoles,
  searchMode,
  isLoading,
  isPlaceholderData,
  hasSearch,
  error,
  page,
  onPageChange,
}: Props) => {
  const { t } = useTranslation()
  const combinedItems = buildResultItems(
    practitioners,
    organizations,
    practitionerRoles,
    searchMode,
  )
  const totalCount = getTotalCount(
    practitioners,
    organizations,
    practitionerRoles,
    searchMode,
  )
  const totalPages = getTotalPages(
    practitioners,
    organizations,
    practitionerRoles,
    searchMode,
    10,
  )
  const hasResults = combinedItems.length > 0

  if (error) {
    return (
      <div className="ds-u-margin-top--4">
        <Alert variation="error" heading="Error">
          {error instanceof Error
            ? error.message
            : "An error occurred during search"}
        </Alert>
      </div>
    )
  }

  if (!hasSearch) {
    return (
      <div className="ds-u-margin-top--4">
        <Alert heading={t("search.unified.initialPromptHeading")}>
          <NpdMarkdown content={t("search.unified.initialPrompt")} />
        </Alert>
      </div>
    )
  }

  if (isLoading && !isPlaceholderData) {
    return null
  }

  if (!hasResults) {
    return (
      <div className="ds-u-margin-top--4">
        <p>{t("search.unified.noResults")}</p>
      </div>
    )
  }

  return (
    <div className="ds-u-margin-top--4">
      <div
        style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          marginBottom: "1rem",
        }}
      >
        <p className="ds-u-margin--0">
          <strong>{totalCount}</strong> {t("search.unified.resultsFound")}
        </p>
      </div>

      {totalPages > 1 && (
        <div style={{ pointerEvents: isPlaceholderData ? "none" : "auto" }}>
          <Pagination
            currentPage={page}
            onPageChange={(evt, nextPage) => {
              evt.preventDefault()
              evt.stopPropagation()
              onPageChange(nextPage)
            }}
            renderHref={(pageNumber) => {
              const params = new URLSearchParams(window.location.search)
              params.set("page", pageNumber.toString())
              return `?${params.toString()}`
            }}
            totalPages={totalPages}
          />
        </div>
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
        {combinedItems.map((item) => {
          const key = `${item.type}-${item.data.id}`
          return (
            <div key={key}>
              {item.type === "provider" && (
                <ListedPractitioner data={item.data} />
              )}
              {item.type === "organization" && (
                <ListedOrganization data={item.data} />
              )}
              {item.type === "role" && (
                <ListedPractitioner
                  data={
                    {
                      id: extractId(item.data.practitioner?.reference),
                      name: [
                        {
                          text:
                            item.data.practitioner?.display ??
                            t("search.unified.unknownProvider"),
                        },
                      ],
                    } as FHIRPractitioner
                  }
                  organizationName={
                    item.data.organization?.display ?? undefined
                  }
                  organizationId={extractId(item.data.organization?.reference)}
                  taxonomyText={getRoleTaxonomyDisplay(item.data)}
                  searchUrl={`/search${location.search}`}
                />
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}
