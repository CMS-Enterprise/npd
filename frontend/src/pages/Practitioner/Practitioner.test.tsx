import { screen } from "@testing-library/react"
import { MemoryRouter, Route, Routes } from "react-router"
import { beforeEach, describe, expect, it } from "vitest"
import { DEFAULT_PRACTITIONER } from "../../../tests/fixtures"
import {
  mockGlobalFetch,
  type MockResponse,
} from "../../../tests/mockGlobalFetch"
import { render } from "../../../tests/render"
import type { FHIRPractitioner } from "../../@types/fhir"
import { Practitioner } from "./Practitioner"

const practitionerApiResponse: MockResponse = [
  "^/fhir/Practitioner/.*",
  DEFAULT_PRACTITIONER,
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
  describe("without PRACTITIONER_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      mockGlobalFetch([practitionerApiResponse])
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
  })

  describe("with PRACTITIONER_LOOKUP_DETAILS feature flag", () => {
    beforeEach(() => {
      mockGlobalFetch([practitionerApiResponse])
    })

    it("shows detailed content", async () => {
      render(<RoutedPractitioner path="/practitioners/12345" />, {
        settings: { feature_flags: { PRACTITIONER_LOOKUP_DETAILS: true } },
      })

      const nameElement = await screen.findByTestId("practitioner-name")

      expect(nameElement).toHaveTextContent(EXPECTED_NAME)
      await screen.findByText("About", { selector: "section h2" })
      await screen.findByText("Contact information", { selector: "section h2" })
      await screen.findByText("Identifiers", { selector: "section h2" })
      await screen.findByText("Taxonomy", { selector: "section h2" })
    })
  })
})
