import { screen, fireEvent } from "@testing-library/react"
import { describe, expect, it, vi, beforeEach } from "vitest"
import { render } from "../../tests/render"
import { UnifiedSearchForm } from "./UnifiedSearchForm"

const makeProps = (
  overrides: Partial<Parameters<typeof UnifiedSearchForm>[0]> = {},
) => ({
  values: { providerName: "", organizationName: "", npi: "", location: "" },
  onChange: vi.fn(),
  onSearch: vi.fn(),
  onClear: vi.fn(),
  isLoading: false,
  ...overrides,
})

describe("UnifiedSearchForm", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("renders all four labeled inputs", () => {
    render(<UnifiedSearchForm {...makeProps()} />)
    expect(screen.getByLabelText(/provider name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/organization/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/npi number/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/location/i)).toBeInTheDocument()
  })

  it("renders the search and clear buttons", () => {
    render(<UnifiedSearchForm {...makeProps()} />)
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /clear/i })).toBeInTheDocument()
  })

  it("disables the submit button when all fields are empty", () => {
    render(<UnifiedSearchForm {...makeProps()} />)
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).toBeDisabled()
  })

  it("enables the submit button when providerName is filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "Smith",
            organizationName: "",
            npi: "",
            location: "",
          },
        })}
      />,
    )
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).not.toBeDisabled()
  })

  it("enables the submit button when organizationName is filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "",
            organizationName: "General Hospital",
            npi: "",
            location: "",
          },
        })}
      />,
    )
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).not.toBeDisabled()
  })

  it("enables the submit button when npi is filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "",
            organizationName: "",
            npi: "1234567894",
            location: "",
          },
        })}
      />,
    )
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).not.toBeDisabled()
  })

  it("keeps submit button disabled when only location is filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "",
            organizationName: "",
            npi: "",
            location: "CA",
          },
        })}
      />,
    )
    expect(
      screen.getByRole("button", { name: /search providers/i }),
    ).toBeDisabled()
  })

  it("shows location hint alert when only location is filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "",
            organizationName: "",
            npi: "",
            location: "CA",
          },
        })}
      />,
    )
    expect(
      screen.getByText(/please also enter a provider name/i),
    ).toBeInTheDocument()
  })

  it("does not show location hint when location and providerName are both filled", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "Smith",
            organizationName: "",
            npi: "",
            location: "CA",
          },
        })}
      />,
    )
    expect(
      screen.queryByText(/please also enter a provider name/i),
    ).not.toBeInTheDocument()
  })

  it("calls onSearch with the current values on form submit", () => {
    const onSearch = vi.fn()
    const values = {
      providerName: "Smith",
      organizationName: "",
      npi: "",
      location: "",
    }
    render(<UnifiedSearchForm {...makeProps({ values, onSearch })} />)
    fireEvent.submit(
      screen
        .getByRole("button", { name: /search providers/i })
        .closest("form")!,
    )
    expect(onSearch).toHaveBeenCalledWith(values)
  })

  it("calls onClear when the Clear button is clicked", () => {
    const onClear = vi.fn()
    render(<UnifiedSearchForm {...makeProps({ onClear })} />)
    fireEvent.click(screen.getByRole("button", { name: /clear/i }))
    expect(onClear).toHaveBeenCalledTimes(1)
  })

  it("disables the submit button and shows 'Searching...' when isLoading is true", () => {
    render(
      <UnifiedSearchForm
        {...makeProps({
          values: {
            providerName: "Smith",
            organizationName: "",
            npi: "",
            location: "",
          },
          isLoading: true,
        })}
      />,
    )
    expect(screen.getByRole("button", { name: /searching/i })).toBeDisabled()
  })
})
