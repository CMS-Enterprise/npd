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

  test("unified search form is displayed at /search", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")

    await expect(page.getByRole("heading", { name: "Search Providers" })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /provider name/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /npi number/i })).toBeVisible()
  })

  test("search button is disabled with no input at /search", async ({ page }) => {
    await page.goto("/search")

    await expect(page.getByRole("button", { name: /search providers/i })).toBeDisabled()
  })

  test("navigating to /search shows unified search form with all inputs", async ({ page }) => {
    await page.goto("/search")

    await expect(page.getByRole("textbox", { name: /provider name/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /organization/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /npi number/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /location/i })).toBeVisible()
  })
})
