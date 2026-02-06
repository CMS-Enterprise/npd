import { createContext } from "react"

export interface SearchContextValue<T> {
  initialQuery?: string
  data: T[] | null
  isLoading: boolean
  isBackgroundLoading: boolean
  error: string | null
  pagination?: PaginationState
  query?: string
  sort: string
}

export interface SearchDispatchContextValue {
  setQuery: (nameOrId: string) => void
  navigateToPage: (page: number) => void
  setSort: (sort: string) => void
  clearSearch: () => void
}

export const SearchContext = createContext<SearchContextValue<unknown> | undefined>(undefined)
export const SearchDispatchContext = createContext<SearchDispatchContextValue | undefined>(undefined)