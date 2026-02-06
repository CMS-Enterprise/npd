import { screen, within } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it } from "vitest"
import { DEFAULT_ORGANIZATION } from "../../../tests/fixtures"
import {
  mockGlobalFetch,
  type MockResponse,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import { Organization } from "./Organization"

const orgApiResponse: MockResponse = [
  "^/fhir/Organization/.*",
  DEFAULT_ORGANIZATION,
]

const RoutedOrganization = ({ path }: { path: string }) => {
  return (
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route
          path="/organizations/:organizationId"
          element={<Organization />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe("Organization", () => {
  describe("without ORGANIZATION_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      mockGlobalFetch([orgApiResponse])
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: false } },
      })

      // ensure FeatureFlag components have finished loading
      await screen.findByText("Content not available")

      expect(screen.queryByText("About", { selector: "section h2" })).toBeNull()
    })
  })

  describe("with ORGANIZATION_LOOKUP_DETAILS feature flag", () => {
    it("shows detailed content", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      // ensure FeatureFlag components have finished loading
      await screen.findByText("Are you the practitioner listed?")

      expect(
        screen.queryByText("About", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Contact information", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Identifiers", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).toBeInTheDocument()
    })
  })
})

describe("identifiers section", () => {
  beforeEach(() => {
    mockGlobalFetch([orgApiResponse])
  })

  it("displays identifiers table when identifiers exist", async () => {
    render(<RoutedOrganization path="/organizations/12345" />, {
      settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
    })

    await screen.findByText("Are you the practitioner listed?")

    const table = screen.getByRole("table")
    expect(table).toBeInTheDocument()

    expect(
      within(table).getByText("Type", { selector: "th" }),
    ).toBeInTheDocument()
    expect(
      within(table).getByText("Number", { selector: "th" }),
    ).toBeInTheDocument()
    expect(
      within(table).getByText("Details", { selector: "th" }),
    ).toBeInTheDocument()
  })
})
