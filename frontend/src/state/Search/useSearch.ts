import { useContext } from "react"
import {
  SearchContext,
  SearchDispatchContext,
  type SearchContextValue,
  type SearchDispatchContextValue,
} from "./SearchContext"

export function useSearchState<T>(): SearchContextValue<T> {
  const context = useContext(SearchContext)
  if (context === undefined) {
    throw new Error("useSearchState must be used within a SearchProvider")
  }
  return context as SearchContextValue<T>
}

export const useSearchDispatch = (): SearchDispatchContextValue => {
  const context = useContext(SearchDispatchContext)
  if (context === undefined) {
    throw new Error("useSearchDispatch must be used within a SearchProvider")
  }
  return context
}
