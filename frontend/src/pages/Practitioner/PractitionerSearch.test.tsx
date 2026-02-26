import { screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { PractitionerSearch } from "./PractitionerSearch"

const RoutedPractitionerSearch = () => (
  <MemoryRouter initialEntries={["/practitioners/search"]}>
    <Routes>
      <Route path="/practitioners/search" element={<PractitionerSearch />} />
    </Routes>
  </MemoryRouter>
)

describe("PractitionerSearch", () => {
  it("renders without crashing", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.getByRole("textbox")).toBeInTheDocument()
  })

  it("renders the page title", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.getByText(/practitioner search/i)).toBeInTheDocument()
  })

  it("renders the search input with label", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.getByRole("textbox", { name: /name or npi/i })).toBeInTheDocument()
    expect(screen.getByLabelText(/name or npi/i)).toBeInTheDocument()
  })

  it("renders the search button", () => {
    render(<RoutedPractitionerSearch />)

    const searchButton = screen.getByRole("button", { name: /search/i })
    expect(searchButton).toBeInTheDocument()
  })

  it("disables search button when input is empty", () => {
    render(<RoutedPractitionerSearch />)

    const searchButton = screen.getByRole("button", { name: /search/i })
    expect(searchButton).toBeDisabled()
  })

  it("renders the initial alert before search", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.getByRole("region")).toBeInTheDocument() 
  })

  it("does not show sort dropdown before search", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.queryByText(/sort by/i)).not.toBeInTheDocument()
  })

  it("does not show search results before search", () => {
    render(<RoutedPractitionerSearch />)

    expect(screen.queryByTestId("searchresults")).not.toBeInTheDocument()
  })
})
