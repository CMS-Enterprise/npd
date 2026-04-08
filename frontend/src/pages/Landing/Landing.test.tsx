import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Landing } from "./Landing"

describe("Landing", () => {
  it("renders landing page content", async () => {
    render(<Landing />)
    expect(
      screen.getByText("National Provider Directory", { selector: "h1" }),
    ).toBeInTheDocument()
  })

  it("renders the tagline", () => {
    render(<Landing />)
    expect(
      screen.getByText(
        "Building the infrastructure for a modern healthcare experience",
      ),
    ).toBeInTheDocument()
  })

  it("renders search the data link", () => {
    render(<Landing />)
    const link = screen.getByRole("link", { name: "Search the data" })
    expect(link).toHaveAttribute("href", "/search")
  })

  it("renders developer documentation link", () => {
    render(<Landing />)
    const link = screen.getByRole("link", { name: "Developer documentation" })
    expect(link).toHaveAttribute("href", "/developers")
  })

  it("renders the mission heading", () => {
    render(<Landing />)
    expect(
      screen.getByText(
        "Finding care should be simple; accurate data makes it possible",
      ),
    ).toBeInTheDocument()
  })

  it("renders the three cards", () => {
    render(<Landing />)
    expect(screen.getByText("Explore the directory")).toBeInTheDocument()
    expect(screen.getByText("For providers")).toBeInTheDocument()
    expect(screen.getByText("For developers")).toBeInTheDocument()
  })
})
