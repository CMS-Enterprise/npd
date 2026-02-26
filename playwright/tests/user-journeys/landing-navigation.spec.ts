import { expect, test } from "@playwright/test"

test.describe("Landing Page → Search Page Navigation", () => {
  test("navigate from landing page to search hub", async ({ page }) => {
    // start at the landing page
    await page.goto("/")
    await expect(page).toHaveURL("/")

    await expect(page.getByRole("heading", { level: 1 })).toBeVisible()
    await page.getByRole("link", { name: /search/i }).first().click()

    await expect(page).toHaveURL("/search")
  })

  test("search hub displays both resource type options", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")

    const practitionerButton = page.getByRole("link", { name: /practitioner/i })
    const organizationButton = page.getByRole("link", { name: /organization/i })

    await expect(practitionerButton).toBeVisible()
    await expect(organizationButton).toBeVisible()

    await expect(practitionerButton).toHaveAttribute("href", "/practitioners/search")
    await expect(organizationButton).toHaveAttribute("href", "/organizations/search")
  })

  test("search hub practitioner button navigates correctly", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("link", { name: /practitioner/i }).click()
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()
  })

  test("search hub organization button navigates correctly", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("link", { name: /organization/i }).click()
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()
  })
})
