import { screen, within } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it, afterEach } from "vitest"
import {
  DEFAULT_ORGANIZATION,
  DEFAULT_PRACTITIONER,
  DEFAULT_LOCATION,
  DEFAULT_PRACTITIONERROLE,
  DEFAULT_ENDPOINT,
  EMPTY_BUNDLE,
  DEFAULT_PRACTITIONERROLE_NOENDPOINTS,
} from "../../../tests/fixtures"
import {
  mockGlobalFetch,
  type MockResponse,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import type { FHIRPractitioner } from "../../@types/fhir"
import { Practitioner } from "./Practitioner"
import { vi } from "vitest"

const practitionerApiResponse: MockResponse = [
  "^/fhir/Practitioner/.*",
  DEFAULT_PRACTITIONER,
]

const practitionerRoleApiResponse: MockResponse = [
  "^/fhir/PractitionerRole/.*",
  DEFAULT_PRACTITIONERROLE,
]

const practitionerRoleApiResponseNoEndpoints: MockResponse = [
  "^/fhir/PractitionerRole/.*",
  DEFAULT_PRACTITIONERROLE_NOENDPOINTS,
]

const emptyPractitionerRoleApiResponse: MockResponse = [
  "^/fhir/PractitionerRole/.*",
  EMPTY_BUNDLE,
]

const organizationApiResponse: MockResponse = [
  "^/fhir/Organization/.*",
  DEFAULT_ORGANIZATION,
]

const locationApiResponse: MockResponse = [
  "^/fhir/Location/.*",
  DEFAULT_LOCATION,
]

const endpointApiResponse: MockResponse = [
  "^/fhir/Endpoint/.*",
  DEFAULT_ENDPOINT,
]

const EXPECTED_NPI =
  (DEFAULT_PRACTITIONER as FHIRPractitioner)["identifier"]?.[0]?.value ||
  "EXPECTED_NPI IS UNSET FIXME"
const EXPECTED_NAME =
  (DEFAULT_PRACTITIONER as FHIRPractitioner)["name"]?.[0]?.text ||
  "EXPECTED_NAME IS UNSET FIXME"
const PRIMARY_LOCATION_NAME = "0006 Aspen Glen Court"
const PRIMARY_LOCATION_ADDRESS = "0006 Aspen Glen Court, Edwards, CO 81632"
const SECONDARY_LOCATION_ID = "secondary-location-id"
const SECONDARY_LOCATION_NAME = "North Clinic"
const SECONDARY_LOCATION_ADDRESS = "200 Market Street, Denver, CO 80205"

const practitionerRoleWithAdditionalLocation = {
  ...DEFAULT_PRACTITIONERROLE,
  results: {
    ...DEFAULT_PRACTITIONERROLE.results,
    entry: [
      ...(DEFAULT_PRACTITIONERROLE.results.entry ?? []),
      {
        fullUrl: `/fhir/PractitionerRole/${SECONDARY_LOCATION_ID}`,
        resource: {
          ...DEFAULT_PRACTITIONERROLE.results.entry?.[0]?.resource,
          id: `${SECONDARY_LOCATION_ID}-role`,
          location: [{ reference: `/fhir/Location/${SECONDARY_LOCATION_ID}` }],
          telecom: [
            {
              system: "phone",
              value: "555-555-5555",
              use: "work",
            },
          ],
        },
      },
    ],
  },
}

const secondaryLocationResponse: MockResponse = [
  `^/fhir/Location/${SECONDARY_LOCATION_ID}/?$`,
  {
    ...DEFAULT_LOCATION,
    id: SECONDARY_LOCATION_ID,
    name: SECONDARY_LOCATION_NAME,
    address: {
      ...DEFAULT_LOCATION.address,
      line: ["200 Market Street"],
      city: "Denver",
      state: "CO",
      postalCode: "80205",
    },
    telecom: [
      {
        system: "phone",
        value: "555-777-8888",
        use: "work",
      },
    ],
  },
]

const RoutedPractitioner = ({ path }: { path: string }) => {
  return (
    <MemoryRouter initialEntries={[path]}>
      <Routes>
        <Route
          path="/practitioners/:practitionerId"
          element={<Practitioner />}
        />
      </Routes>
    </MemoryRouter>
  )
}

describe("Practitioner", () => {
  describe("with full data attribution", () => {
    beforeEach(() => {
      mockGlobalFetch([
        practitionerApiResponse,
        practitionerRoleApiResponse,
        organizationApiResponse,
        locationApiResponse,
        endpointApiResponse,
      ])
    })

    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: false } },
      })

      // ensure loading has finished
      await screen.findByRole("heading", { name: EXPECTED_NAME })

      expect(screen.queryByText(`NPI: ${EXPECTED_NPI}`)).not.toBeInTheDocument()
      expect(screen.getByText("Not verified")).toBeInTheDocument()
      expect(
        screen.queryByText("About", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByRole("button", { name: "Report an issue" }),
      ).not.toBeInTheDocument()
    })
    it("shows detailed content when feature flag is set", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      expect(screen.getAllByText("Internal Medicine").length).toBeGreaterThan(0)
      expect(screen.getByText("Not verified")).toBeInTheDocument()
      await screen.findByText("Basic information", { selector: "section h2" })
      expect(screen.getByText("NPI")).toBeInTheDocument()
      expect(screen.getByText(EXPECTED_NPI)).toBeInTheDocument()
      expect(
        screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(
        screen.getByRole("button", { name: "Claim this record" }),
      ).toBeInTheDocument()
      expect(
        screen.getByRole("button", { name: "Report issue with this record" }),
      ).toBeInTheDocument()
      expect(
        await screen.getByText("555-555-5555", { exact: false }),
      ).toBeInTheDocument()
      expect(
        screen.queryByText("Organization(s)", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("Endpoint(s)", { selector: "section h4" }),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("Location(s)", { selector: "section h4" }),
      ).not.toBeInTheDocument()
      expect(
        screen.getByText("Locations", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(screen.getByText("Acme Healthcare System")).toBeInTheDocument()
      expect(screen.getByText(PRIMARY_LOCATION_ADDRESS)).toBeInTheDocument()
      expect(screen.queryByText("Fax")).not.toBeInTheDocument()
      expect(
        screen.queryByText("Identifiers", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(screen.queryByText(/Medicare Provider/i)).not.toBeInTheDocument()
      expect(
        screen.queryByText("jane.smith@acmehealthcare.com"),
      ).not.toBeInTheDocument()
      expect(screen.queryByText(/Office Hours/i)).not.toBeInTheDocument()
    })

    it("renders the feedback CTA", async () => {
      render(
        <RoutedPractitioner path="/practitioners/without-organization" />,
        {
          settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
        },
      )

      await screen.findByTestId("practitioner-name")

      expect(
        screen.getByText(
          "Let us know if you see any problems with this provider record.",
        ),
      ).toBeInTheDocument()
      expect(
        screen.getByRole("button", { name: "Report issue with this record" }),
      ).toBeInTheDocument()
    })

    describe("feedback form", () => {
      afterEach(() => {
        vi.resetAllMocks()
      })

      it("displays the practitioner name inside the form dialog", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([
          practitionerApiResponse,
          practitionerRoleApiResponse,
          organizationApiResponse,
          locationApiResponse,
          endpointApiResponse,
        ])

        render(<RoutedPractitioner path="/practitioners/12345" />, {
          settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
        })

        await screen.findByTestId("practitioner-name")

        await user.click(
          screen.getByRole("button", { name: "Report issue with this record" }),
        )

        const dialog = screen.getByRole("dialog")
        expect(dialog).toBeInTheDocument()
        expect(within(dialog).getByText(EXPECTED_NAME)).toBeInTheDocument()
      })

      it("enables submit when 'Other' is selected and details are provided", async () => {
        const user = userEvent.setup()

        mockGlobalFetch([
          practitionerApiResponse,
          practitionerRoleApiResponse,
          organizationApiResponse,
          locationApiResponse,
          endpointApiResponse,
        ])

        render(<RoutedPractitioner path="/practitioners/12345" />, {
          settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
        })

        await screen.findByTestId("practitioner-name")

        await user.click(
          screen.getByRole("button", { name: "Report issue with this record" }),
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

  describe("without organization relationships", () => {
    beforeEach(() => {
      mockGlobalFetch([
        practitionerApiResponse,
        emptyPractitionerRoleApiResponse,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("shows detailed content without organization information", async () => {
      render(<RoutedPractitioner path="/practitioners/extra-locations" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      await screen.findByText("Basic information", { selector: "section h2" })
      expect(screen.getByText("NPI")).toBeInTheDocument()
      expect(screen.getByText(EXPECTED_NPI)).toBeInTheDocument()
      expect(
        screen.queryByText("Identifiers", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(screen.getAllByText("Internal Medicine").length).toBeGreaterThan(0)
      expect(
        screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("Organization(s)", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(screen.getAllByText("—").length).toBeGreaterThan(0)
      expect(
        screen.getByText("Locations", { selector: "section h2" }),
      ).toBeInTheDocument()
    })
  })

  describe("without endpoints", () => {
    beforeEach(() => {
      mockGlobalFetch([
        practitionerApiResponse,
        practitionerRoleApiResponseNoEndpoints,
        organizationApiResponse,
        locationApiResponse,
      ])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("shows detailed content without endpoint information", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      expect(
        screen.queryByText("About", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      await screen.findByText("Basic information", { selector: "section h2" })
      expect(screen.getByText(EXPECTED_NPI)).toBeInTheDocument()
      expect(
        screen.queryByText("Identifiers", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(screen.getAllByText("Internal Medicine").length).toBeGreaterThan(0)
      expect(
        screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).not.toBeInTheDocument()
      expect(
        await screen.getByText(PRIMARY_LOCATION_ADDRESS),
      ).toBeInTheDocument()
      expect(
        await screen.getByText("555-555-5555", { exact: false }),
      ).toBeInTheDocument()
      expect(screen.queryByText("Fax")).not.toBeInTheDocument()
      expect(
        screen.queryByText("Endpoint(s)", { selector: "section h4" }),
      ).not.toBeInTheDocument()
      expect(
        screen.queryByText("No endpoint information available"),
      ).not.toBeInTheDocument()
    })
  })

  describe("with additional locations", () => {
    beforeEach(() => {
      mockGlobalFetch([
        practitionerApiResponse,
        ["^/fhir/PractitionerRole/.*", practitionerRoleWithAdditionalLocation],
        organizationApiResponse,
        secondaryLocationResponse,
        locationApiResponse,
      ])
    })

    afterEach(() => {
      vi.resetAllMocks()
    })

    it("shows all provider locations including the primary practice location", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      await screen.findByTestId("practitioner-name")

      expect(
        await screen.findByText("Locations", { selector: "section h2" }),
      ).toBeInTheDocument()
      const locationsSection = screen
        .getByText("Locations", { selector: "section h2" })
        .closest("section")
      expect(locationsSection).toBeTruthy()
      expect(
        within(locationsSection as HTMLElement).getByText(
          SECONDARY_LOCATION_NAME,
        ),
      ).toBeInTheDocument()
      expect(
        within(locationsSection as HTMLElement).getByText(
          SECONDARY_LOCATION_ADDRESS,
        ),
      ).toBeInTheDocument()
      expect(
        within(locationsSection as HTMLElement).getAllByText(
          "Acme Healthcare System",
        ).length,
      ).toBeGreaterThan(0)
      expect(
        within(locationsSection as HTMLElement).getAllByRole("link", {
          name: "1234567890",
        })[0],
      ).toHaveAttribute("href", "/organizations/12345")
      expect(
        within(locationsSection as HTMLElement).getByText(
          PRIMARY_LOCATION_NAME,
        ),
      ).toBeInTheDocument()
      expect(
        within(locationsSection as HTMLElement).getByText(
          PRIMARY_LOCATION_ADDRESS,
        ),
      ).toBeInTheDocument()
    })
  })
})
