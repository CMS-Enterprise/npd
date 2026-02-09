import { expect, test } from "@playwright/test"
import { ORGANIZATION } from "../constants"

let organization = ORGANIZATION

// load a known practitioner record from the API before running tests
test.beforeAll(async ({ request }) => {
  const response = await request.get(
    "/fhir/Organization/?identifier=1234567893",
  )
  const payload = await response.json()
  const resource = payload.results.entry[0].resource

  organization = {
    id: resource.id,
    name: resource.name,
    npi: resource.identifier[0].value,
  }

  expect(organization).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: "AAA Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Organization Journey", () => {
  test("landing -> search hub -> organization search -> detail view", async ({ page }) => {
    // start at landing page
    await page.goto("/")
    await expect(page).toHaveURL("/")

    // then, navigate to search hub
    await page.getByRole("link", { name: /search/i }).first().click()
    await expect(page).toHaveURL("/search")

    // then, select Organization search
    await page.getByRole("link", { name: /organization/i }).click()
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    // then, perform search by NPI
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567893")
    await page.getByRole("button", { name: "Search" }).click()

    // then, confirm search results appear
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()

    // then, click on organization to view details
    await page.getByRole("link", { name: "AAA Test Org" }).click()

    // finally, confirm detail page content
    await expect(page).toHaveURL(`/organizations/${organization.id}`)

    const banner = page.locator("section.banner")
    await expect(banner.getByText("Provider group")).toBeVisible()
    await expect(banner.getByText(organization.name)).toBeVisible()
    await expect(banner.getByText(`NPI: ${organization.npi}`)).toBeVisible()
  })

  test("landing -> last page -> organization detail", async ({ page }) => {
    await page.goto("/")
  
    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /organization/i }).click()
  
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("TEST")
    await page.getByRole("button", { name: "Search" }).click()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toContainText("Name (A-Z)")
    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()
    await expect(sortButton).toContainText("Name (Z-A)")
  
    await page.getByLabel("Next Page").first().click()
    await expect(page).toHaveURL(/page=2/)
    
    const responsePromise = page.waitForResponse("**/fhir/Organization")
    await page.getByLabel("Next Page").first().click()
    const response = await responsePromise;
  
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
    await page.getByRole("link", { name: "AAA Test Org" }).click()
  
    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    await expect(page.locator("div[role='heading']")).toContainText(organization.name)
  })

  test("organization journey with partial name search", async ({ page }) => {
    await page.goto("/")

    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /organization/i }).click()

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
    await page.getByRole("link", { name: "AAA Test Org" }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
  })

  test("organization journey with sorting functionality", async ({ page }) => {
    await page.goto("/")

    await page.getByRole("link", { name: /search/i }).first().click()
    await page.getByRole("link", { name: /organization/i }).click()

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()

    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(sortButton).toContainText("Name (Z-A)")

    await page.getByRole("link", { name: /TEST/ }).first().click()

    const banner = page.locator("section.banner")
    await expect(banner.getByText(/TEST/)).toBeVisible()
  })
})
