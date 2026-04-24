import { screen, within, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it, afterEach } from "vitest"
import {
  DEFAULT_ORGANIZATION,
  DEFAULT_PRACTITIONERROLE,
  DEFAULT_PRACTITIONER,
  EMPTY_BUNDLE,
  DEFAULT_LOCATIONS,
  DEFAULT_ENDPOINT,
  DEFAULT_LOCATIONS_NOENDPOINTS,
} from "../../../tests/fixtures"
import {
  mockGlobalFetch,
  type MockResponse,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import { Organization } from "./Organization"
import { vi } from "vitest"

const orgApiResponse: MockResponse = [
  "^/fhir/Organization/.*",
  DEFAULT_ORGANIZATION,
]

const practitionerRoleApiResponse: MockResponse = [
  "^/fhir/PractitionerRole/.*",
  DEFAULT_PRACTITIONERROLE,
]

const emptyPractitionerRoleApiResponse: MockResponse = [
  "^/fhir/PractitionerRole/.*",
  EMPTY_BUNDLE,
]

const practitionerApiResponse: MockResponse = [
  "^/fhir/Practitioner/.*",
  DEFAULT_PRACTITIONER,
]

const locationsApiResponse: MockResponse = [
  "^/fhir/Location/.*",
  DEFAULT_LOCATIONS,
]

const locationsApiResponseNoEndpoints: MockResponse = [
  "^/fhir/Location/.*",
  DEFAULT_LOCATIONS_NOENDPOINTS,
]

const emptyLocationsApiResponse: MockResponse = [
  "^/fhir/Location/.*",
  EMPTY_BUNDLE,
]

const endpointApiResponse: MockResponse = [
  "^/fhir/Endpoint/.*",
  DEFAULT_ENDPOINT,
]

const EXPECTED_ORG_NAME =
  (DEFAULT_ORGANIZATION as { name?: string })["name"] ||
  "EXPECTED_ORG_NAME IS UNSET FIXME"

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
  describe("with full data attribution", () => {
    beforeEach(() => {
      mockGlobalFetch([
        orgApiResponse,
        practitionerRoleApiResponse,
        practitionerApiResponse,
        locationsApiResponse,
        endpointApiResponse,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: false } },
      })

      await waitFor(() => screen.findByText("Content not available"))

      expect(screen.queryByText("Basic Information")).not.toBeInTheDocument()
    })

    it("shows detailed content with the ORGANIZATION_LOOKUP_DETAILS feature flag", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      await screen.findByTestId("organization-name")

      expect(
        screen.getByText("Basic Information", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("Practice Locations", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("CMS Aligned Networks", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("Data Exchange Endpoints", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("Authorized Official", { selector: "h3" }),
      ).toBeInTheDocument()
      expect(
        screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).toBeInTheDocument()
      expect(
        screen.getByText("555-555-5555", { exact: false }),
      ).toBeInTheDocument()
      expect(screen.getByText("fhir.test-org.org")).toBeInTheDocument()
      expect(screen.getByText("HL7 FHIR")).toBeInTheDocument()
      expect(
        screen.queryByText("Contact information not available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No location information available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No endpoint information available"),
      ).not.toBeInTheDocument()
      expect(
        screen.getByText(
          "No CMS aligned networks on record for this organization.",
        ),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("No practitioner information available"),
      ).not.toBeInTheDocument()
    })

    it("renders the feedback CTA", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      await screen.findByTestId("organization-name")

      expect(
        screen.getByText(
          "Found incorrect information? Let us know so we can update this record.",
        ),
      ).toBeInTheDocument()
      expect(
        screen.getByRole("button", { name: "Report Issue with This Record" }),
      ).toBeInTheDocument()
    })

    describe("feedback form", () => {
      afterEach(() => {
        vi.resetAllMocks()
      })

      it("displays the organization name inside the form dialog", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([
          orgApiResponse,
          practitionerRoleApiResponse,
          practitionerApiResponse,
          locationsApiResponse,
          endpointApiResponse,
        ])

        render(<RoutedOrganization path="/organizations/12345" />, {
          settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
        })

        await screen.findByTestId("organization-name")

        await user.click(
          screen.getByRole("button", {
            name: "Report Issue with This Record",
          }),
        )

        const dialog = screen.getByRole("dialog")
        expect(dialog).toBeInTheDocument()
        expect(within(dialog).getByText(EXPECTED_ORG_NAME)).toBeInTheDocument()
      })

      it("enables submit when 'Other' is selected and details are provided", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([
          orgApiResponse,
          practitionerRoleApiResponse,
          practitionerApiResponse,
          locationsApiResponse,
          endpointApiResponse,
        ])

        render(<RoutedOrganization path="/organizations/12345" />, {
          settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
        })

        await screen.findByTestId("organization-name")

        await user.click(
          screen.getByRole("button", {
            name: "Report Issue with This Record",
          }),
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

  describe("without practitioner role data", () => {
    beforeEach(() => {
      mockGlobalFetch([
        orgApiResponse,
        emptyPractitionerRoleApiResponse,
        locationsApiResponse,
        endpointApiResponse,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render practitioner table", async () => {
      render(<RoutedOrganization path="/organizations/1234567" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      expect(
        await screen.findByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).toBeInTheDocument()

      expect(
        screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).toBeInTheDocument()
      expect(
        screen.getByText("555-555-5555", { exact: false }),
      ).toBeInTheDocument()
      expect(screen.getByText("fhir.test-org.org")).toBeInTheDocument()
      expect(screen.getByText("HL7 FHIR")).toBeInTheDocument()
      expect(
        screen.queryByText("Contact information not available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No location information available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No endpoint information available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No practitioner information available"),
      ).not.toBeInTheDocument()
    })
  })

  describe("without endpoint data", () => {
    beforeEach(() => {
      mockGlobalFetch([
        orgApiResponse,
        emptyPractitionerRoleApiResponse,
        locationsApiResponseNoEndpoints,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render endpoint table", async () => {
      render(<RoutedOrganization path="/organizations/123456" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      expect(
        await screen.findByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).toBeInTheDocument()

      expect(
        screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).toBeInTheDocument()
      expect(
        screen.getByText("555-555-5555", { exact: false }),
      ).toBeInTheDocument()
      expect(screen.queryByText("fhir.test-org.org")).not.toBeInTheDocument()
      expect(screen.queryByText("HL7 FHIR")).not.toBeInTheDocument()
      expect(
        screen.queryByText("Contact information not available"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No location information available"),
      ).not.toBeInTheDocument()
      expect(
        screen.getByText("No endpoint information available."),
      ).toBeInTheDocument()
    })
  })

  describe("without location data", () => {
    beforeEach(() => {
      mockGlobalFetch([
        orgApiResponse,
        emptyPractitionerRoleApiResponse,
        emptyLocationsApiResponse,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render location or endpoint table", async () => {
      render(<RoutedOrganization path="/organizations/123450" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      expect(
        await screen.findByText("No practice location information available."),
      ).toBeInTheDocument()

      expect(
        screen.queryByText("0006 Aspen Glen Court, Edwards, CO 81632"),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("555-555-5555", { exact: false }),
      ).not.toBeInTheDocument()
      expect(screen.queryByText("fhir.test-org.org")).not.toBeInTheDocument()
      expect(screen.queryByText("HL7 FHIR")).not.toBeInTheDocument()
      expect(
        screen.queryByText("Contact information not available"),
      ).not.toBeInTheDocument()
      expect(
        screen.getByText("No practice location information available."),
      ).toBeInTheDocument()
      expect(
        screen.getByText("No endpoint information available."),
      ).toBeInTheDocument()
    })
  })
})
