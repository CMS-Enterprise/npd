import { expect, test as setup } from "@playwright/test"

const authFile = "tests/.auth/user.json"

setup("authenticate", async ({ page }) => {
  // Perform authentication steps. Replace these actions with your own.
  await page.goto("/accounts/login/")
  await expect(page).toHaveURL("/accounts/login/")
  await expect(page.locator("#login-form")).toBeVisible()
  await page.getByLabel("Username").fill("developer@cms.hhs.gov")
  await page.getByLabel("Password").fill("password123")
  await page.getByRole("button", { name: "Sign in" }).click()

  // Wait until the page receives the cookies.
  //
  // Sometimes login flow sets cookies in the process of several redirects.
  // Wait for the final URL to ensure that the cookies are actually set.
  await page.waitForURL("/")

  // End of authentication steps.

  await page.context().storageState({ path: authFile })
})
