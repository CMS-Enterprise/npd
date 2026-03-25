import { screen, render } from "@testing-library/react"
import { describe, expect, it, vi } from "vitest"
import { FeedbackCTA } from "./FeedbackCTA"

const defaultProps = {
  subtitle: "Let us know if something looks wrong.",
  onButtonClick: vi.fn(),
}

const renderFeedbackCTA = (overrides = {}) =>
  render(<FeedbackCTA {...defaultProps} {...overrides} />)

describe("FeedbackCTA", () => {
  it("renders the heading", () => {
    renderFeedbackCTA()
    expect(screen.getByText("Help improve the directory")).toBeInTheDocument()
  })

  it("renders the subtitle", () => {
    renderFeedbackCTA()
    expect(
      screen.getByText("Let us know if something looks wrong."),
    ).toBeInTheDocument()
  })

  it("renders the button", () => {
    renderFeedbackCTA()
    expect(
      screen.getByRole("button", { name: "Report an issue" }),
    ).toBeInTheDocument()
  })

  it("renders the button as disabled when isDisabled is true", () => {
    renderFeedbackCTA({ isDisabled: true })
    expect(
      screen.getByRole("button", { name: "Report an issue" }),
    ).toBeDisabled()
  })
})
