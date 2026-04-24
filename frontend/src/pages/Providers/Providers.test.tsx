import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Providers } from "./Providers"

describe("Providers", () => {
  it("renders the page heading", () => {
    render(<Providers />)
    expect(
      screen.getByText("Information for providers", {
        selector: "[role=heading]",
      }),
    ).toBeInTheDocument()
  })

  it("renders all section headings from content", () => {
    render(<Providers />)

    expect(
      screen.getByText("For all providers", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Leveraging what you've already shared", {
        selector: "h1",
      }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Connecting to vital services", { selector: "h1" }),
    ).toBeInTheDocument()
  })

  it("renders provider directory description", () => {
    render(<Providers />)

    expect(
      screen.getByText(
        /The National Provider Directory aims to be the authoritative source/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
  })

  it("renders data sharing content", () => {
    render(<Providers />)

    expect(
      screen.getByText(/The Directory is built on a combination of data/, {
        selector: "p",
      }),
    ).toBeInTheDocument()
  })

  it("renders vital services content", () => {
    render(<Providers />)

    expect(
      screen.getByText(/By consolidating provider data and addresses/, {
        selector: "p",
      }),
    ).toBeInTheDocument()
  })

  it("renders back to top link", () => {
    render(<Providers />)
    expect(screen.getByText("Back to top")).toBeInTheDocument()
  })

  it("renders link to About page", () => {
    render(<Providers />)
    const link = screen.getByRole("link", { name: "About page" })
    expect(link).toHaveAttribute("href", "/about")
  })
})
