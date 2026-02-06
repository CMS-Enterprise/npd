import { screen } from "@testing-library/react"
import { MemoryRouter } from "react-router"
import { describe, expect, it } from "vitest"
import { render } from "../../../tests/render"
import { Search } from "./Search"

const renderSearch = () => {
  render(
    <MemoryRouter>
      <Search />
    </MemoryRouter>
  )
}

describe("Search", () => {
  it("renders the page title", () => {
    renderSearch()
    expect(screen.getByText("Search the data")).toBeInTheDocument()
  })

  it("renders the subtitle text", () => {
    renderSearch()
    expect(
      screen.getByText(
        "Search by name or NPI number to see the details of any practitioner or organization in the database."
      )
    ).toBeInTheDocument()
  })

  it("renders the practitioner search button", () => {
    renderSearch()
    const practitionerButton = screen.getByRole("link", { name: /practitioner search/i })
    expect(practitionerButton).toBeInTheDocument()
    expect(practitionerButton).toHaveAttribute("href", "/practitioners/search")
  })

  it("renders the organization search button", () => {
    renderSearch()
    const organizationButton = screen.getByRole("link", { name: /organization search/i })
    expect(organizationButton).toBeInTheDocument()
    expect(organizationButton).toHaveAttribute("href", "/organizations/search")
  })
})