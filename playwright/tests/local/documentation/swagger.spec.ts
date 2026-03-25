import { expect, test } from "@playwright/test"
import { FHIR_RESOURCES } from "../constants"

test.describe("Swagger", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/fhir/docs/")

    await expect(page.getByText("NPD FHIR API")).toBeVisible()
    await expect(page.getByRole("link", { name: "/fhir/docs/schema/" })).toBeVisible()
    await expect(page.locator("section").filter({ hasText: "Authorize" })).toBeVisible()
  })

  test("displays all FHIR resource tags", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    for (const resource of FHIR_RESOURCES) {
      const tag = page.getByRole("link", { name: resource, exact: true })
      await expect(tag).toBeVisible()
    }
  })

  test("regression test: 'search' parameter should not appear in any endpoint", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    // check Organization endpoint
    await page.getByRole("button", { name: "GET /fhir/Organization/", exact: true }).click()
    await expect(page.getByText("GET/fhir/Organization/ Query")).toBeVisible()

    const orgSection = page.locator("section").filter({ hasText: "GET/fhir/Organization/" })
    await expect(orgSection.locator("tr[data-param-name]").first()).toBeAttached()
    await expect(orgSection.locator("tr[data-param-name='search']")).not.toBeAttached()

    // check Practitioner endpoint
    await page.getByRole("button", { name: "GET /fhir/Practitioner/", exact: true }).click()
    await expect(page.getByText("GET/fhir/Practitioner/ Query")).toBeVisible()

    const practitionerSection = page.locator("section").filter({ hasText: "GET/fhir/Practitioner/" })
    await expect(practitionerSection.locator("tr[data-param-name]").first()).toBeAttached()
    await expect(practitionerSection.locator("tr[data-param-name='search']")).not.toBeAttached()
  })
})

test.describe("Swagger - Organization", () => {
  test("GET /fhir/Organization/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Organization/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Organization/{id}/", async ({ page }) => {
    // First get a valid organization ID
    const orgResponse = await page.request.get("/fhir/Organization/?identifier=NPI|1234567893")
    const orgData = await orgResponse.json()
    const orgId = orgData.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Organization/{id}/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()

    await page.locator("tr[data-param-name='id'] input").fill(orgId)
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - Practitioner", () => {
  test("GET /fhir/Practitioner/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Practitioner/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Practitioner/{id}/", async ({ page }) => {
    // First get a valid practitioner ID
    const response = await page.request.get("/fhir/Practitioner/?identifier=NPI|1234567894")
    const data = await response.json()
    const practitionerId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Practitioner/{id}/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()

    await page.locator("tr[data-param-name='id'] input").fill(practitionerId)
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - Location", () => {
  test("GET /fhir/Location/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Location/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

//   test("GET /fhir/Location/{id}/", async ({ page }) => {
//     we dont have any locations currently in test database
//   })
})

test.describe("Swagger - Endpoint", () => {
  test("GET /fhir/Endpoint/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Endpoint/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Endpoint/{id}/", async ({ page }) => {
    // First get a valid endpoint ID
    const response = await page.request.get("/fhir/Endpoint/")
    const data = await response.json()
    const endpointId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/Endpoint/{id}/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()

    await page.locator("tr[data-param-name='id'] input").fill(endpointId)
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - PractitionerRole", () => {
  test("GET /fhir/PractitionerRole/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/PractitionerRole/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

//   test("GET /fhir/PractitionerRole/{id}/", async ({ page }) => {
//     // we dont have any PractitionerRoles currently in test database
//   })
})

test.describe("Swagger - metadata", () => {
  test("GET /fhir/metadata/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.getByText("NPD FHIR API")).toBeVisible()

    await page.getByRole("button", { name: "GET /fhir/metadata/", exact: true }).click()
    await page.getByRole("button", { name: "Try it out" }).click()
    await page.getByRole("button", { name: "Execute" }).click()

    const liveResponse = page.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})