import { useMemo } from "react"
import { useSearchParams, type SetURLSearchParams } from "react-router"
import type { FHIRCollection } from "../@types/fhir"

type SupportedParams = RequiredPaginationParams & SearchParams

const DEFAULT_PAGE_SIZE = 10

const toInt = (value: string | null | undefined, fallback: number): number => {
  if (typeof value === "undefined" || value === null) return fallback

  const pval = parseInt(value)
  return isNaN(pval) ? fallback : pval
}

const coercePaginationParams = (params: URLSearchParams): SupportedParams => {
  const out: SupportedParams = {
    page: toInt(params.get("page"), 1),
    page_size: toInt(params.get("page_size"), DEFAULT_PAGE_SIZE),
  }

  const query = params.get("query")
  if (query !== null) {
    out.query = query
  }

  const sort = params.get("sort")
  if (sort !== null) {
    out.sort = sort
  }

  return out
}

export const usePaginationParams = (): [
  SupportedParams,
  SetURLSearchParams,
] => {
  const [search, setSearch] = useSearchParams()

  return [coercePaginationParams(search), setSearch]
}

export const usePagination = (
  pagination: SupportedParams,
  data: undefined | FHIRCollection<unknown>,
): PaginationState => {
  return useMemo(() => {
    let totalPages = 1
    let total = 0
    let count = 0

    if (data) {
      totalPages = Math.ceil(data.count / pagination.page_size)
      total = data.results.total
      count = data.count
    }

    return {
      ...pagination,
      total,
      count,
      totalPages,
    }
  }, [data, pagination])
}
