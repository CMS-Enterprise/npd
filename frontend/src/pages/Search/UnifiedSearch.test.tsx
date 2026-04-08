import { screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { describe, expect, it, beforeEach } from "vitest"
import { render } from "../../../tests/render"
import { mockGlobalFetch } from "../../../tests/mockGlobalFetch"
import { UnifiedSearch } from "./UnifiedSearch"

const RoutedUnifiedSearch = () => (
  <MemoryRouter initialEntries={["/search"]}>
    <Routes>
      <Route path="/search" element={<UnifiedSearch />} />
    </Routes>
  </MemoryRouter>
)

describe("UnifiedSearch", () => {
  beforeEach(() => {
    mockGlobalFetch()
  })

  it("renders the page title", () => {
    render(<RoutedUnifiedSearch />)
    expect(
      screen.getByRole("heading", { name: "Search Providers" }),
    ).toBeInTheDocument()
  })

  it("renders all four form inputs", () => {
    render(<RoutedUnifiedSearch />)
    expect(screen.getByLabelText(/provider name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/organization/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/npi number/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument()
  })

  it("renders the submit button in disabled state initially", () => {
    render(<RoutedUnifiedSearch />)
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).toBeDisabled()
  })

  it("renders the Clear button", () => {
    render(<RoutedUnifiedSearch />)
    expect(screen.getByRole("button", { name: /clear/i })).toBeInTheDocument()
  })

  it("shows the initial prompt alert when no search has been submitted", () => {
    render(<RoutedUnifiedSearch />)
    expect(
      screen.getByRole("heading", { name: /^search$/i }),
    ).toBeInTheDocument()
  })

  it("does not show search results before a search is submitted", () => {
    render(<RoutedUnifiedSearch />)
    expect(screen.queryByTestId("searchresults")).not.toBeInTheDocument()
  })
})
