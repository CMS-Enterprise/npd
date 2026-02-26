import { expect, test } from "@playwright/test"
import { FHIR_RESOURCES } from "../constants"

test.describe("Swagger", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/fhir/docs/")

    await expect(page.locator("#swagger-ui")).toBeVisible()
    await expect(page.locator(".info .title")).toContainText("NPD FHIR API")
  })

  test("displays all FHIR resource tags", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    for (const resource of FHIR_RESOURCES) {
      const tag = page.locator(`h3.opblock-tag[data-tag="${resource}"]`)
      await expect(tag).toBeVisible()
    }
  })

  test("regression test: 'search' parameter should not appear in any endpoint", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    // check Organization endpoint
    const orgOperation = page.locator("#operations-Organization-Organization_list")
    await orgOperation.locator(".opblock-summary-control").click()
    await expect(orgOperation.locator(".opblock-body")).toBeVisible()

    await expect(orgOperation.locator("tr[data-param-name]").first()).toBeAttached()
    await expect(orgOperation.locator("tr[data-param-name='search']")).not.toBeAttached()
  
    // check Practitioner endpoint
    const practitionerOperation = page.locator("#operations-Practitioner-Practitioner_list")
    await practitionerOperation.locator(".opblock-summary-control").click()
    await expect(practitionerOperation.locator(".opblock-body")).toBeVisible()

    await expect(practitionerOperation.locator("tr[data-param-name]").first()).toBeAttached()
    await expect(practitionerOperation.locator("tr[data-param-name='search']")).not.toBeAttached()
  })
})

test.describe("Swagger - Organization", () => {
  test("GET /fhir/Organization/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Organization-Organization_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Organization/{id}/", async ({ page }) => {
    // First get a valid organization ID
    const orgResponse = await page.request.get("/fhir/Organization/?identifier=1234567893")
    const orgData = await orgResponse.json()
    const orgId = orgData.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Organization-Organization_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(orgId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - Practitioner", () => {
  test("GET /fhir/Practitioner/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Practitioner-Practitioner_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Practitioner/{id}/", async ({ page }) => {
    // First get a valid practitioner ID
    const response = await page.request.get("/fhir/Practitioner/?identifier=1234567894")
    const data = await response.json()
    const practitionerId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Practitioner-Practitioner_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(practitionerId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - Location", () => {
  test("GET /fhir/Location/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Location-Location_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

//   test("GET /fhir/Location/{id}/", async ({ page }) => {
//     we dont have any locations currently in test database
//   })
})

test.describe("Swagger - Endpoint", () => {
  test("GET /fhir/Endpoint/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Endpoint-Endpoint_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

  test("GET /fhir/Endpoint/{id}/", async ({ page }) => {
    // First get a valid endpoint ID
    const response = await page.request.get("/fhir/Endpoint/")
    const data = await response.json()

    const endpointId = data.results.entry[0].resource.id

    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-Endpoint-Endpoint_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()

    await operation.locator("tr[data-param-name='id'] input").fill(endpointId)
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})

test.describe("Swagger - PractitionerRole", () => {
  test("GET /fhir/PractitionerRole/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-PractitionerRole-PractitionerRole_list")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })

//   test("GET /fhir/PractitionerRole/{id}/", async ({ page }) => {
//     // we dont have any PractitionerRoles currently in test database
//   })
})

test.describe("Swagger - metadata", () => {
  test("GET /fhir/metadata/", async ({ page }) => {
    await page.goto("/fhir/docs/")
    await expect(page.locator("#swagger-ui")).toBeVisible()

    const operation = page.locator("#operations-metadata-metadata_retrieve")
    await operation.locator(".opblock-summary-control").click()
    await operation.locator(".try-out__btn").click()
    await operation.locator(".execute").click()

    const liveResponse = operation.locator(".live-responses-table tbody .response-col_status")
    await expect(liveResponse).toContainText("200")
  })
})