import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { About } from "./About"

describe("About", () => {
  it("renders the page heading", () => {
    render(<About />)
    expect(
      screen.getByText("About the directory", { selector: "[role=heading]" }),
    ).toBeInTheDocument()
  })

  it("renders all section headings from content", () => {
    render(<About />)

    expect(
      screen.getByText("What is the National Provider Directory?", {
        selector: "h1",
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("How to search for providers", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Long-term vision", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Building the foundation together", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Accounts and secure authentication options", {
        selector: "h1",
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Release notes", { selector: "h1" }),
    ).toBeInTheDocument()
  })

  it("renders introductory content", () => {
    render(<About />)

    expect(
      screen.getByText(
        /The National Provider Directory \(NPD\) beta is a first step/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
  })

  it("renders auth cards section", () => {
    render(<About />)

    expect(screen.getByText("ID.me")).toBeInTheDocument()
    expect(screen.getByText("CLEAR")).toBeInTheDocument()
    expect(screen.getByText("Login.gov")).toBeInTheDocument()
  })

  it("renders back to top link", () => {
    render(<About />)
    expect(screen.getByText("Back to top")).toBeInTheDocument()
  })
})
