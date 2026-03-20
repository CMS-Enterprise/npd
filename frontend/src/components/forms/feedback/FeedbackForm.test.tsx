import { screen, render } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { FeedbackForm } from "./FeedbackForm"

vi.mock("./Altcha", () => ({
  Altcha: vi.fn(() => <div data-testid="altcha-mock" />),
}))

const defaultProps = {
  presenterData: { recordName: "Jane S. Smith", npi: "1234567891" },
  onExit: vi.fn(),
  isOpen: true,
}

const renderForm = (overrides = {}) =>
  render(<FeedbackForm {...defaultProps} {...overrides} />)

describe("FeedbackForm", () => {
  it("renders the dialog heading", () => {
    renderForm()
    expect(screen.getByText("Report an issue")).toBeInTheDocument()
  })

  it("renders the provider name", () => {
    renderForm()
    expect(screen.getByText("Jane S. Smith")).toBeInTheDocument()
  })

  it("renders all issue checkboxes", () => {
    renderForm()
    expect(screen.getByLabelText("Practice location(s)")).toBeInTheDocument()
    expect(screen.getByLabelText("Phone number(s)")).toBeInTheDocument()
    expect(
      screen.getByLabelText("Taxonomy(-ies)/specialty(-ies)"),
    ).toBeInTheDocument()
    expect(
      screen.getByLabelText("Organization affiliation (s)"),
    ).toBeInTheDocument()
    expect(screen.getByLabelText("FHIR endpoint")).toBeInTheDocument()
    expect(screen.getByLabelText("Missing information")).toBeInTheDocument()
    expect(screen.getByLabelText("Other (specify below)")).toBeInTheDocument()
  })

  it("renders the details textarea", () => {
    renderForm()
    expect(
      screen.getByLabelText(/Please provide details about the issue/),
    ).toBeInTheDocument()
  })

  it("renders the email field", () => {
    renderForm()
    expect(screen.getByLabelText("Email address")).toBeInTheDocument()
  })

  it("renders the privacy notice", () => {
    renderForm()
    expect(screen.getByText("Privacy notice")).toBeInTheDocument()
  })

  it("renders the CAPTCHA widget", () => {
    renderForm()
    expect(screen.getByTestId("altcha-mock")).toBeInTheDocument()
  })

  it("renders Cancel and Submit buttons", () => {
    renderForm()
    expect(screen.getByRole("button", { name: "Cancel" })).toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Submit" })).toBeInTheDocument()
  })

  it("renders Submit as disabled when no issues are selected", () => {
    renderForm()
    expect(screen.getByRole("button", { name: "Submit" })).toBeDisabled()
  })

  it("does not render the form when isOpen is false", () => {
    renderForm({ isOpen: false })
    expect(screen.queryByText("Report an issue")).not.toBeInTheDocument()
  })
})
