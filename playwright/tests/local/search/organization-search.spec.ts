import { expect, test } from "@playwright/test"
import { ORGANIZATION } from "../constants"

let organization = ORGANIZATION

// load a known organization record from the API before running tests
test.beforeAll(async ({ request }) => {
  // expects a FhirCollection<FhirOrganization> API response
  const response = await request.get(
    "/fhir/Organization/?identifier=NPI|1234567893",
  )
  const payload = await response.json()

  const resource = payload.results.entry[0].resource

  organization = {
    id: resource.id,
    name: resource.name,
    npi: resource.identifier[0].value,
  }

  // it should look like the /fhir/Organization/ record created by seedsystem
  expect(organization).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: "AAA Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Search", () => {
  test("search for an Organization by NPI", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "NPI" })
      .fill("1234567893")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by exact name", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "Organization" })
      .click()
    await page
      .getByRole("textbox", { name: "Organization" })
      .fill("AAA Test Org")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by partial name", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "Organization" })
      .click()
    await page
      .getByRole("textbox", { name: "Organization" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for a Organization and confirm pagination works", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByText("Search Providers")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Organization" })
      .click()
    await page
      .getByRole("textbox", { name: "Organization" })
      .fill("TEST")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Org/i })).toBeVisible()
    await expect(page.getByRole("caption")).toContainText(
      "Showing 1 - 10 of 26",
    )

    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(10)

    await page.getByLabel("Next Page").first().click()

    await expect(page).toHaveURL(/page=2/)
    await expect(page.getByRole("caption")).toContainText(
      "Showing 11 - 20 of 26",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(10)

    await page.getByLabel("Next Page").first().click()

    await expect(page).toHaveURL(/page=3/)
    await expect(page.locator("span[role='caption']")).toContainText(
      "Showing 21 - 26 of 26",
    )
    await expect(
      page.locator("[data-testid='searchresults']").getByRole("listitem"),
    ).toHaveCount(6)
  })
})