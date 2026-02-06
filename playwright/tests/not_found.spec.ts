import { expect, test } from "@playwright/test"

test.describe("while signed in", () => {
  test("invalid route renders not found page", async ({ page }) => {
    await page.goto("/not/a/real/path")
    await expect(page).toHaveURL("/not/a/real/path")
    await expect(page.locator("section h2")).toContainText("Page not found")
  })
})
