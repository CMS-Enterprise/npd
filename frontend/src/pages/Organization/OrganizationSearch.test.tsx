import { screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { OrganizationSearch } from "./OrganizationSearch"

const RoutedOrganizationSearch = () => (
  <MemoryRouter initialEntries={["/organizations/search"]}>
    <Routes>
      <Route path="/organizations/search" element={<OrganizationSearch />} />
    </Routes>
  </MemoryRouter>
)

describe("OrganizationSearch", () => {
  it("renders without crashing", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.getByRole("textbox")).toBeInTheDocument()
  })

  it("renders the page title", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.getByText(/organization search/i)).toBeInTheDocument()
  })

  it("renders the search input with label", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.getByRole("textbox", { name: /name or npi/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/name or npi/i)).toBeInTheDocument()
  })

  it("renders the search button", () => {
    render(<RoutedOrganizationSearch />)

    const searchButton = screen.getByRole("button", { name: /search/i })
    expect(searchButton).toBeInTheDocument()
  })

  it("disables search button when input is empty", () => {
    render(<RoutedOrganizationSearch />)

    const searchButton = screen.getByRole("button", { name: /search/i })
    expect(searchButton).toBeDisabled()
  })

  it("renders the initial alert before search", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.getByRole("region")).toBeInTheDocument() 
  })

  it("does not show sort dropdown before search", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.queryByText(/sort by/i)).not.toBeInTheDocument()
  })

  it("does not show search results before search", () => {
    render(<RoutedOrganizationSearch />)

    expect(screen.queryByTestId("searchresults")).not.toBeInTheDocument()
  })
})
