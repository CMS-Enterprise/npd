import { expect, test } from "@playwright/test"
import { FHIR_RESOURCES } from "../constants"

test.describe("Redoc", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")

    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()
  })

  test("displays all FHIR resource sections in navigation", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    for (const resource of FHIR_RESOURCES) {
      const navItem = page.locator("label").filter({ hasText: new RegExp(`^${resource}$`) })
      await expect(navItem).toBeVisible()
    }
  })

  // regression test: "search" parameter should not appear in any endpoint
  test("does not display invalid 'search' parameter", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    // check Organization endpoint
    const orgSection = page.locator('[id="operation/Organization_list"]')
    await expect(orgSection.getByRole("heading", { name: "query Parameters" })).toBeVisible()
    await expect(orgSection.locator("td").filter({ hasText: /^search$/ })).not.toBeVisible()

    // check Practitioner endpoint
    const practitionerSection = page.locator('[id="operation/Practitioner_list"]')
    await expect(practitionerSection.getByRole("heading", { name: "query Parameters" })).toBeVisible()
    await expect(practitionerSection.locator("td").filter({ hasText: /^search$/ })).not.toBeVisible()
  })

  test("can navigate to Organization section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^Organization$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/Organization Organization" })).toBeVisible()
  })

  test("can navigate to Practitioner section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^Practitioner$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/Practitioner Practitioner" })).toBeVisible()
  })

  test("can navigate to Location section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^Location$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/Location Location" })).toBeVisible()
  })

  test("can navigate to Endpoint section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^Endpoint$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/Endpoint Endpoint" })).toBeVisible()
  })

  test("can navigate to PractitionerRole section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^PractitionerRole$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/PractitionerRole PractitionerRole" })).toBeVisible()
  })

  test("can navigate to metadata section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.getByRole("heading", { name: "NPD FHIR API (beta)" })).toBeVisible()

    await page.locator("label").filter({ hasText: /^metadata$/ }).click()

    await expect(page.getByRole("heading", { name: "tag/metadata metadata" })).toBeVisible()
  })
})