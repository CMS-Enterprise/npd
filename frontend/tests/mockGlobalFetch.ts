import { vi } from "vitest"
import type { Organization } from "../src/@types/fhir/Organization"
import type { Practitioner } from "../src/@types/fhir/Practitioner"
import { DEFAULT_FRONTEND_SETTINGS } from "./fixtures"

export const settingsResponseWithFeature = (
  flagValues: Record<string, boolean>,
  previous?: FrontendSettings,
): MockResponse => {
  const settings = previous || DEFAULT_FRONTEND_SETTINGS
  return [
    "^/api/frontend_settings$",
    {
      ...settings,
      feature_flags: {
        ...settings.feature_flags,
        ...flagValues,
      },
    },
  ]
}

type UrlMatch = string
// new API response types should be added as a union to ApiResponseType
type ApiResponseType = FrontendSettings | Organization | Practitioner

export type MockResponse = [UrlMatch, ApiResponseType]

// Mock the global fetch function, allow tests to define custom responses
export const mockGlobalFetch = (requests?: MockResponse[]) => {
  global.fetch = vi.fn<typeof global.fetch>((input: RequestInfo | URL) => {
    // look for a custom response, if it exists, use it
    const found = requests?.find((entry) => {
      const path = entry[0]

      if (path.startsWith("^") && typeof input === "string") {
        return new RegExp(path.slice(1)).test(input)
      }

      return input === path
    })

    if (found) {
      const response = found[1]
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(response),
      } as Response)
    }

    // handle default responses
    if (typeof input === "string" && input.endsWith("/api/frontend_settings")) {
      return Promise.resolve({
        ok: true,
        json: () => Promise.resolve(DEFAULT_FRONTEND_SETTINGS),
      } as Response)
    }

    // unhandled API request
    return Promise.resolve({
      ok: false,
      json: () => Promise.resolve({}),
    } as Response)
  })
}
