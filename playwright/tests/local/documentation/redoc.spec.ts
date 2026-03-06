import { expect, test } from "@playwright/test"
import { FHIR_RESOURCES } from "../constants"

test.describe("Redoc", () => {
  test("loads successfully", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")

    await expect(page.locator(".redoc-wrap")).toBeVisible()
    await expect(page.locator(".api-info h1")).toBeVisible()
  })

  test("displays all FHIR resource sections in navigation", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    for (const resource of FHIR_RESOURCES) {
      const navItem = page.locator(`li[data-item-id="tag/${resource}"]`)
      await expect(navItem).toBeVisible()
    }
  })

  // regression test: "search" parameter should not appear in any endpoint
  test("does not display invalid 'search' parameter", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    // check Organization endpoint
    const orgSection = page.locator("#tag\\/Organization\\/operation\\/Organization_list")
    await expect(orgSection.getByText("query Parameters")).toBeVisible()
    await expect(orgSection.locator("td").filter({ hasText: /^search$/ })).not.toBeVisible()

    // check Practitioner endpoint
    const practitionerSection = page.locator("#tag\\/Practitioner\\/operation\\/Practitioner_list")
    await expect(practitionerSection.getByText("query Parameters")).toBeVisible()
    await expect(practitionerSection.locator("td").filter({ hasText: /^search$/ })).not.toBeVisible()

  })

  test("can navigate to Organization section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/Organization"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/Organization h2")).toBeVisible()
  })

  test("can navigate to Practitioner section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/Practitioner"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/Practitioner h2")).toBeVisible()
  })

  test("can navigate to Location section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/Location"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/Location h2")).toBeVisible()
  })

  test("can navigate to Endpoint section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/Endpoint"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/Endpoint h2")).toBeVisible()
  })

  test("can navigate to PractitionerRole section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/PractitionerRole"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/PractitionerRole h2")).toBeVisible()
  })

  test("can navigate to metadata section", async ({ page }) => {
    await page.goto("/fhir/docs/redoc/")
    await expect(page.locator(".redoc-wrap")).toBeVisible()

    const navItem = page.locator('li[data-item-id="tag/metadata"] > label')
    await navItem.click()

    await expect(page.locator("#tag\\/metadata h2")).toBeVisible()
  })

})
