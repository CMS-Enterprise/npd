import { expect, test } from "@playwright/test"

// do not use / don't overwrite default authentication session
test.use({ storageState: { cookies: [], origins: [] } })

test("local dev default account can sign in and sign out", async ({ page }) => {
  // act: click on "Sign in" link in header
  await page.goto("")
  await page.getByRole("link", { name: "Sign in" }).click()

  // assert: we're looking at the login screen
  await expect(page).toHaveURL("/accounts/login/")
  await expect(page.locator("#login-form")).toBeVisible()
  await expect(page.locator("form legend")).toContainText("Sign in")

  // act: sign in
  await page.getByLabel("Username").fill("developer@cms.hhs.gov")
  await page.getByLabel("Password").fill("password123")
  await page.getByRole("button", { name: "Sign in" }).click()

  // assert: redirection after successful sign-in sends user to the landing
  // page with updated header
  await expect(page).toHaveURL("/")
  await expect(page.locator("form#authentication-form")).toContainText(
    "Sign out",
  )
  await expect(page.locator("h1")).toContainText("National Provider Directory")

  // act: sign out
  await page.getByRole("button", { name: "Sign out" }).click()

  // assert: redirection after sign-out sends user to sign-in page
  await page.waitForURL("/accounts/login/")
  await expect(page.locator("nav [role=navigation] a")).toContainText("Sign in")
})
