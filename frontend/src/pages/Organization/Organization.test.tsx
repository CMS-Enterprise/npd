import { screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router"
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest"
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

const EXPECTED_ORGANIZATION_NAME =
  DEFAULT_ORGANIZATION.name || "EXPECTED_ORGANIZATION_NAME IS UNSET FIXME"

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
    beforeEach(() => {
      mockGlobalFetch([orgApiResponse])
    })

    afterEach(() => {
      vi.resetAllMocks()
    })

    it("shows detailed content", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      // ensure FeatureFlag components have finished loading
      await screen.findByText("About")

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

    it("renders the feedback CTA", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      await screen.findByText("About")

      expect(
        screen.getByText(
          "Let us know if you see any problems with this provider record.",
        ),
      ).toBeInTheDocument()
      expect(
        screen.getByRole("button", { name: "Report an issue" }),
      ).toBeInTheDocument()
    })

    describe("feedback form", () => {
      it("displays the organization name inside the form dialog", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([orgApiResponse])

        render(<RoutedOrganization path="/organizations/12345" />, {
          settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
        })

        await screen.findByText("About")

        await user.click(
          screen.getByRole("button", { name: "Report an issue" }),
        )

        const dialog = screen.getByRole("dialog")
        expect(dialog).toBeInTheDocument()
        expect(
          within(dialog).getByText(EXPECTED_ORGANIZATION_NAME),
        ).toBeInTheDocument()
      })

      it("enables submit when 'Other' is selected and details are provided", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([orgApiResponse])

        render(<RoutedOrganization path="/organizations/12345" />, {
          settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
        })

        await screen.findByText("About")

        await user.click(
          screen.getByRole("button", { name: "Report an issue" }),
        )

        const dialog = screen.getByRole("dialog")
        expect(dialog).toBeInTheDocument()

        const otherCheckbox = within(dialog).getByRole("checkbox", {
          name: /other/i,
        })
        await user.click(otherCheckbox)

        const detailsInput = within(dialog).getByRole("textbox", {
          name: /details/i,
        })
        await user.type(detailsInput, "Additional details about the issue")

        expect(
          within(dialog).getByRole("button", { name: /submit/i }),
        ).not.toBeDisabled()
      })
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

    await screen.findByText("About")

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

describe("taxonomy section", () => {
  beforeEach(() => {
    mockGlobalFetch([orgApiResponse])
  })

  it("shows taxonomy data when extensions exist", async () => {
    render(<RoutedOrganization path="/organizations/12345" />, {
      settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
    })

    const taxonomyHeading = await screen.findByText("Taxonomy", {
      selector: "section h2",
    })
    const taxonomySection = taxonomyHeading.closest("section")!

    expect(
      within(taxonomySection).getByText("Pediatric Clinic"),
    ).toBeInTheDocument()
  })
})
