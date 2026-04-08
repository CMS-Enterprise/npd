import { describe, expect, it } from "vitest"
import { getSearchMode } from "./unifiedSearch"

describe("getSearchMode", () => {
  it("returns 'none' when all params are empty", () => {
    expect(getSearchMode({})).toBe("none")
  })

  it("returns 'none' when all params are undefined", () => {
    expect(
      getSearchMode({
        providerName: undefined,
        organizationName: undefined,
        npi: undefined,
        location: undefined,
      }),
    ).toBe("none")
  })

  it("returns 'providers' when only providerName is set", () => {
    expect(getSearchMode({ providerName: "Smith" })).toBe("providers")
  })

  it("returns 'organizations' when only organizationName is set", () => {
    expect(getSearchMode({ organizationName: "General Hospital" })).toBe(
      "organizations",
    )
  })

  it("returns 'npi-lookup' when only npi is set", () => {
    expect(getSearchMode({ npi: "1234567894" })).toBe("npi-lookup")
  })

  it("returns 'cross-entity' when both providerName and organizationName are set", () => {
    expect(
      getSearchMode({
        providerName: "Smith",
        organizationName: "General Hospital",
      }),
    ).toBe("cross-entity")
  })

  it("returns 'providers' when providerName and location are set", () => {
    expect(getSearchMode({ providerName: "Smith", location: "CA" })).toBe(
      "providers",
    )
  })

  it("returns 'npi-lookup' when npi and location are set", () => {
    expect(getSearchMode({ npi: "1234567894", location: "12345" })).toBe(
      "npi-lookup",
    )
  })

  it("returns 'cross-entity' when providerName, organizationName, and npi are all set", () => {
    expect(
      getSearchMode({
        providerName: "Smith",
        organizationName: "General Hospital",
        npi: "1234567894",
      }),
    ).toBe("cross-entity")
  })
})
