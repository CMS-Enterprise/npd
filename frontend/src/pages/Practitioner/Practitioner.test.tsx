import { screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it, afterEach } from "vitest"
import { DEFAULT_ORGANIZATION, DEFAULT_PRACTITIONER, DEFAULT_LOCATION, DEFAULT_PRACTITIONERROLE, DEFAULT_ENDPOINT, EMPTY_BUNDLE, DEFAULT_PRACTITIONERROLE_NOENDPOINTS } from "../../../tests/fixtures"
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
      mockGlobalFetch([practitionerApiResponse, practitionerRoleApiResponse, organizationApiResponse, locationApiResponse, endpointApiResponse])
    })

    afterEach(() => {
      vi.resetAllMocks()
    })

    it("does not render content when feature flag is unset", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: false } },
      })

      // ensure loading has finished
      await screen.findByText(EXPECTED_NAME)

      expect(screen.queryByText(`NPI: ${EXPECTED_NPI}`)).toBeInTheDocument()
      expect(
        screen.queryByText("About", { selector: "section h2" }),
      ).not.toBeInTheDocument()
    })
    it("shows detailed content when feature flag is set", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      await screen.findByText("About", { selector: "section h2" })
      await screen.findByText("Contact information", { selector: "section h2" })
      expect(await screen.findByText(/8170 33rd Ave S Stop 21110Q\s+Bloomington, MN 55425/)).toBeInTheDocument()
      await screen.findByText("Identifiers", { selector: "section h2" })
      await screen.findByText("Taxonomy", { selector: "section h2" })

      expect(await screen.getByText("207R00000X")).toBeInTheDocument()
      expect(await screen.getByText("Internal Medicine")).toBeInTheDocument()
      await screen.findByText("Organization(s)", { selector: "section h2" })
      await screen.findByText("Endpoint(s)", { selector: "section h4" })
      await screen.findByText("Locations", { selector: "section h4" })
      expect(await screen.getByText("Acme Healthcare System (NPI: 1234567890)")).toBeInTheDocument()
      expect(await screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632")).toBeInTheDocument()
      expect (await screen.getByText("555-555-5555", {exact: false})).toBeInTheDocument()
      expect (await screen.getByText("fhir.test-org.org")).toBeInTheDocument()
      expect (await screen.getByText("HL7 FHIR")).toBeInTheDocument()
      expect(await screen.queryByText("Contact information not available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No location information available")).not.toBeInTheDocument()
      expect(await screen.queryByText("No endpoint information available")).not.toBeInTheDocument()
      
    })
  })

  describe("without organization relationships", () => {
    beforeEach(() => {
      mockGlobalFetch([practitionerApiResponse, emptyPractitionerRoleApiResponse])
    })
     afterEach(() => {
      vi.resetAllMocks()
    })
    
    it("shows detailed content without organization information", async () => {

      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      await screen.findByText("About", { selector: "section h2" })
      await screen.findByText("Contact information", { selector: "section h2" })
      expect(await screen.findByText(/8170 33rd Ave S Stop 21110Q\s+Bloomington, MN 55425/)).toBeInTheDocument()
      await screen.findByText("Identifiers", { selector: "section h2" })
      await screen.findByText("Taxonomy", { selector: "section h2" })
      expect(await screen.getByText("207R00000X")).toBeInTheDocument()
      expect(await screen.getByText("Internal Medicine")).toBeInTheDocument()
      await screen.findByText("Organization(s)", { selector: "section h2" })
      expect (await screen.getByText("No organization relationship found")).toBeInTheDocument()
    })
  })

  describe("without endpoints", () => {
    beforeEach(() => {
      mockGlobalFetch([practitionerApiResponse, practitionerRoleApiResponseNoEndpoints, organizationApiResponse, locationApiResponse])
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
      await screen.findByText("About", { selector: "section h2" })
      await screen.findByText("Contact information", { selector: "section h2" })
      expect(await screen.findByText(/8170 33rd Ave S Stop 21110Q\s+Bloomington, MN 55425/)).toBeInTheDocument()
      await screen.findByText("Identifiers", { selector: "section h2" })
      await screen.findByText("Taxonomy", { selector: "section h2" })
      expect(await screen.getByText("207R00000X")).toBeInTheDocument()
      expect(await screen.getByText("Internal Medicine")).toBeInTheDocument()
      await screen.findByText("Organization(s)", { selector: "section h2" })
      await screen.findByText("Endpoint(s)", { selector: "section h4" })
      await screen.findByText("Locations", { selector: "section h4" })
      expect(await screen.getByText("Acme Healthcare System (NPI: 1234567890)")).toBeInTheDocument()
      expect(await screen.getByText("0006 Aspen Glen Court, Edwards, CO 81632")).toBeInTheDocument()
      expect (await screen.getByText("555-555-5555", {exact: false})).toBeInTheDocument()
      expect (await screen.queryByText("fhir.test-org.org")).not.toBeInTheDocument()
      expect (await screen.queryByText("HL7 FHIR")).not.toBeInTheDocument()
      expect(await screen.getByText("No endpoint information available")).toBeInTheDocument()
    })
  })
})
