import { render, screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { Developers } from "./Developers"
import { SidebarMenu } from "./SidebarMenu"

describe("Developers", () => {
  it("renders developer page headings", async () => {
    render(<Developers />)
    expect(
      screen.getByText("Documentation", { selector: "[role=heading]" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("For developers", { selector: "span" }),
    ).toBeInTheDocument()
  })

  it("renders all section headings from content", () => {
    render(<Developers />)

    expect(
      screen.getByText("Participating in the beta", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Providing feedback", { selector: "h2" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("About the data", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Accessing the data", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Overview", { selector: "h2" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Authentication", { selector: "h2" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Available endpoints", { selector: "h2" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Developer sandbox", { selector: "h1" }),
    ).toBeInTheDocument()
    expect(
      screen.getByText("Open source project", { selector: "h1" }),
    ).toBeInTheDocument()
  })

  it("renders beta participation content", () => {
    render(<Developers />)
    
    expect(
      screen.getByText(
        /This limited beta release provides a select group of early adopters/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
    expect(
      screen.getByText(
        /This site and API are available to you for testing purposes/,
        { selector: "li" },
      ),
    ).toBeInTheDocument()
  })

  it("renders data source information", () => {
    render(<Developers />)
    
    expect(
      screen.getByText(
        /The initial dataset combines data from NPPES, PECOS, CEHRT/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
  })

  it("renders API access information", () => {
    render(<Developers />)
    
    expect(
      screen.getByText(
        /Developers can query and retrieve National Provider Directory data via a REST API/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
  })

  it("renders open source project information", () => {
    render(<Developers />)
    
    expect(
      screen.getByText(
        /The National Provider Directory team is taking an open source approach/,
        { selector: "p" },
      ),
    ).toBeInTheDocument()
  })

})

describe("SidebarMenu", () => {
  it("renders all navigation items", () => {
    render(<SidebarMenu />)
    
    expect(screen.getByText("Participating in the beta")).toBeInTheDocument()
    expect(screen.getByText("Providing feedback")).toBeInTheDocument()
    expect(screen.getByText("About the data")).toBeInTheDocument()
    expect(screen.getByText("Accessing the data")).toBeInTheDocument()
    expect(screen.getByText("Developer sandbox")).toBeInTheDocument()
    expect(screen.getByText("Open source project")).toBeInTheDocument()
  })
})