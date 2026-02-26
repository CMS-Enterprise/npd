import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Landing } from "./Landing"

describe("Landing", () => {
  it("renders landing page content", async () => {
    render(<Landing />)
    expect(
      screen.getByText("National Provider Directory", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(screen.getByText("LIMITED-RELEASE BETA")).toBeInTheDocument()
  })

  it("renders the tagline", () => {
    render(<Landing />)
    expect(
      screen.getByText("Building the new infrastructure for health data interoperability"),
    ).toBeInTheDocument()
  })

  it("renders developer resources link", () => {
    render(<Landing />)
    const link = screen.getByRole("link", { name: "Developer resources" })
    expect(link).toHaveAttribute("href", "/developers")
  })

  it("renders search link", () => {
    render(<Landing />)
    const link = screen.getByRole("link", { name: "Search the data" })
    expect(link).toHaveAttribute("href", "/search")
  })

  it("renders the beta alert", () => {
    render(<Landing />)
    expect(screen.getByText("This project is in beta")).toBeInTheDocument()
  })
})