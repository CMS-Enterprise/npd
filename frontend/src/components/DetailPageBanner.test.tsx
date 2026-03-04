import { screen } from "@testing-library/react"
import { describe, expect, it } from "vitest"
import { render } from "@testing-library/react"
import { DetailPageBanner } from "./DetailPageBanner"

const defaultProps = {
  title: "Jane S. Smith",
  subtitle: "NPI: 1234567891",
  pageType: "Practitioner",
  testIdPrefix: "practitioner",
}

const renderBanner = (overrides = {}) =>
  render(<DetailPageBanner {...defaultProps} {...overrides} />)

describe("DetailPageBanner", () => {
  it("renders the title and subtitle", () => {
    renderBanner()
    expect(screen.getByTestId("practitioner-name")).toHaveTextContent(
      "Jane S. Smith",
    )
    expect(screen.getByTestId("practitioner-npi")).toHaveTextContent(
      "NPI: 1234567891",
    )
  })

  it("renders the resource type label", () => {
    renderBanner()
    expect(screen.getByText("Practitioner")).toBeInTheDocument()
  })

  it("does not render subtitle when not provided", () => {
    renderBanner({ subtitle: undefined })
    expect(screen.queryByTestId("practitioner-npi")).not.toBeInTheDocument()
  })

  it("uses the correct testIdPrefix", () => {
    renderBanner({ testIdPrefix: "organization" })
    expect(screen.getByTestId("organization-name")).toBeInTheDocument()
    expect(screen.getByTestId("organization-npi")).toBeInTheDocument()
  })
})
