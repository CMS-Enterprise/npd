import React, { useEffect, useState, type ReactNode } from "react"
import { usePagination, usePaginationParams } from "../../hooks/usePagination"
import {
  SearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"
import type { FHIRCollection } from "../../@types/fhir"
import type { UseQueryResult } from "@tanstack/react-query"

interface SearchProviderProps<T> {
  children: ReactNode
  useSearchAPI: (
    params: PaginationParams & SearchParams,
    options?: { requireQuery?: boolean }
  ) => UseQueryResult<FHIRCollection<T>>
  defaultSort: string
}

export function SearchProvider<T>({ 
  children, 
  useSearchAPI,
  defaultSort
}: SearchProviderProps<T>) {
  const [isBackgroundLoading, setIsBackgroundLoading] = useState(false)
  const [params, setParams] = usePaginationParams()
  const [query, setQueryValue] = useState<string>(params.query || "")

  const currentSort = params.sort || defaultSort
  
  // the injected hook handles the actual fetching
  const { data, isLoading, error } = useSearchAPI(
    { ...params, sort: currentSort },
    { requireQuery: true }
  )
  
  const pagination = usePagination(params, data)

  const buildParams = (overrides: { page?: string; query?: string; sort?: string }) => {
    const nextQuery = overrides.query ?? params.query ?? query
    const nextSort = overrides.sort ?? currentSort
    
    const next: Record<string, string> = {
      page: overrides.page ?? "1",
      sort: nextSort
    }
    
    if (nextQuery) {
      next.query = nextQuery
    }
    
    return next
  }

  const setQuery = (nextQuery: string) => {
    setIsBackgroundLoading(false)
    setQueryValue(nextQuery)
    const next = buildParams({ page: "1", query: nextQuery })
    setParams(next, { preventScrollReset: true })
  }

  const navigateToPage = (toPage: number) => {
    setIsBackgroundLoading(true)
    const next = buildParams({ page: toPage.toString() })
    setParams(next, { preventScrollReset: true })
  }

  const setSort = (nextSort: string) => {
    setIsBackgroundLoading(true)
    const next = buildParams({ page: "1", sort: nextSort })
    setParams(next, { preventScrollReset: true })
  }

  const clearSearch = () => {
    setQueryValue("")
    setParams({})
  }

  useEffect(() => {
    if (!isLoading) {
      setIsBackgroundLoading(false)
    }
  }, [isLoading])

  const hasActiveQuery = params.query && params.query.length > 0
  
  const state: SearchContextValue<T> = {
    initialQuery: query,
    data: hasActiveQuery && data?.results?.entry
      ? data.results.entry.map((entry) => entry.resource)
      : null,
    isLoading,
    isBackgroundLoading,
    error: error
      ? error instanceof Error
        ? error.message
        : "An error occurred during search"
      : null,
    pagination,
    query,
    sort: currentSort
  }

  const dispatch: SearchDispatchContextValue = {
    setQuery,
    navigateToPage,
    setSort,
    clearSearch,
  }

  return (
    <SearchContext value={state}>
      <SearchDispatchContext value={dispatch}>
        {children}
      </SearchDispatchContext>
    </SearchContext>
  )
}
