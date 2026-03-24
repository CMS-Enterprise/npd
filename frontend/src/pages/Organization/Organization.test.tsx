import { screen, within, waitFor } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it, afterEach } from "vitest"
import { DEFAULT_ORGANIZATION, DEFAULT_PRACTITIONERROLE, DEFAULT_PRACTITIONER, EMPTY_BUNDLE, DEFAULT_LOCATIONS, DEFAULT_ENDPOINT, DEFAULT_LOCATIONS_NOENDPOINTS } from "../../../tests/fixtures"
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
      mockGlobalFetch([orgApiResponse, practitionerRoleApiResponse, practitionerApiResponse, locationsApiResponse, endpointApiResponse])
    })
    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: false } },
      })

      // ensure FeatureFlag components have finished loading
      await waitFor(() => screen.findByText("Content not available"))

      expect(await screen.queryByText("About", { selector: "section h2" })).toBeNull()
    })
    it("shows detailed content with the ORGANIZATION_LOOKUP_DETAILS feature flag", async () => {
      render(<RoutedOrganization path="/organizations/12345" />, {
        settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
      })

      // ensure FeatureFlag and org details components have finished loading
      await waitFor(() => screen.getByTestId('location-table'))

      expect(
      await screen.queryByText("About", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
      await screen.queryByText("Contact information", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
      await screen.queryByText("Identifiers", { selector: "section h2" }),
      ).toBeInTheDocument()
      expect(
      await screen.queryByText("Taxonomy", { selector: "section h2" }),
      ).toBeInTheDocument()

      const table = await screen.getByTestId("identifier-table")
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

      const taxonomyHeading = await screen.findByText("Taxonomy", {
      selector: "section h2",
      })
      const taxonomySection = taxonomyHeading.closest("section")!

      expect(
        within(taxonomySection).getByText("Pediatric Clinic"),
      ).toBeInTheDocument()

      expect(await screen.getByText("DR. KIRK AADALEN")).toBeInTheDocument()
      expect(await screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632")).toBeInTheDocument()
      expect (await screen.getByText("555-555-5555", {exact: false})).toBeInTheDocument()
      expect (await screen.getByText("fhir.test-org.org")).toBeInTheDocument()
      expect (await screen.getByText("HL7 FHIR")).toBeInTheDocument()
      expect(await screen.queryByText("Contact information not available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No location information available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No endpoint information available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No practitioner information available")).not.toBeInTheDocument()
    })
  })
  describe("without practitioner role data", () => {
  beforeEach(() => {
    mockGlobalFetch([orgApiResponse, emptyPractitionerRoleApiResponse, locationsApiResponse, endpointApiResponse])
  })
  afterEach(() => {
      vi.resetAllMocks()
    })

  it("does not render practitioner table", async () => {
    render(<RoutedOrganization path="/organizations/1234567" />, {
      settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
    })

      // ensure FeatureFlag and org details components have finished loading
      await waitFor(() => screen.getByTestId('location-table'))
      expect(await screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632")).toBeInTheDocument()
      expect (await screen.getByText("555-555-5555", {exact: false})).toBeInTheDocument()
      expect (await screen.getByText("fhir.test-org.org")).toBeInTheDocument()
      expect (await screen.getByText("HL7 FHIR")).toBeInTheDocument()
      expect(await screen.queryByText("Contact information not available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No location information available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No endpoint information available")).not.toBeInTheDocument()

      expect(await screen.getByText("No practitioner information available")).toBeInTheDocument()
      expect(await screen.queryByText("DR. KIRK AADALEN")).not.toBeInTheDocument()
    
  })
  })
describe("without endpoint data", () => {
  beforeEach(() => {
    mockGlobalFetch([orgApiResponse, emptyPractitionerRoleApiResponse, locationsApiResponseNoEndpoints])
  })
  afterEach(() => {
      vi.resetAllMocks()
    })

  it("does not render endpoint table", async () => {
    render(<RoutedOrganization path="/organizations/123456" />, {
      settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
    })
      // ensure FeatureFlag and org details components have finished loading
      await waitFor(() => screen.getByTestId('location-table'))
      expect(await screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632")).toBeInTheDocument()
      expect (await screen.getByText("555-555-5555", {exact: false})).toBeInTheDocument()
      expect (await screen.queryByText("fhir.test-org.org")).not.toBeInTheDocument()
      expect (await screen.queryByText("HL7 FHIR")).not.toBeInTheDocument()
      expect(await screen.queryByText("Contact information not available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No location information available")).not.toBeInTheDocument()
      expect(await screen.getByText("No endpoint information available")).toBeInTheDocument()

    
  })
  })
  describe("without location data", () => {
  beforeEach(() => {
    mockGlobalFetch([orgApiResponse, emptyPractitionerRoleApiResponse, emptyLocationsApiResponse])
  })
  afterEach(() => {
      vi.resetAllMocks()
    })

  it("does not render location or endpoint table", async () => {
    render(<RoutedOrganization path="/organizations/12345" />, {
      settings: { feature_flags: { ORGANIZATION_LOOKUP_DETAILS: true } },
    })
      // ensure FeatureFlag components have finished loading
      await waitFor(() => screen.findByText("About"))
      expect(await screen.queryByText("0006 Aspen Glen Court, Edwards, CO 81632")).not.toBeInTheDocument()
      expect (await screen.queryByText("555-555-5555", {exact: false})).not.toBeInTheDocument()
      expect (await screen.queryByText("fhir.test-org.org")).not.toBeInTheDocument()
      expect (await screen.queryByText("HL7 FHIR")).not.toBeInTheDocument()
      expect(await screen.queryByText("Contact information not available")).not.toBeInTheDocument()
      expect(await screen.getByText("No location information available")).toBeInTheDocument()
      expect(await screen.getByText("No endpoint information available")).toBeInTheDocument()

    
  })
  })
  })
