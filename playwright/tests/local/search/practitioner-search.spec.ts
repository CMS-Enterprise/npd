import { expect, test } from "@playwright/test"
import { PRACTITIONER } from "../constants"

let practitioner = PRACTITIONER

// load a known practitioner record from the API before running tests
test.beforeAll(async ({ request }) => {
  // expects a FhirCollection<FhirPractitioner> API response
  const response = await request.get(
    "/fhir/Practitioner/?identifier=NPI|1234567894",
  )
  const payload = await response.json()

  const resource = payload.results.entry[0].resource

  // Practitioner names are in resource.name[0].text or constructed from given/family
  const nameRecord = resource.name?.[0]
  const name = nameRecord?.text || `${nameRecord?.given?.[0] || ""} ${nameRecord?.family || ""}`.trim()

  practitioner = {
    id: resource.id,
    name: name,
    npi: resource.identifier?.find(
      (i: { system?: string }) => 
        i.system === "http://hl7.org/fhir/sid/us-npi" || 
        i.system === "http://terminology.hl7.org/NamingSystem/npi"
    )?.value || resource.identifier?.[0]?.value,
  }

  // it should look like the /fhir/Practitioner/ record created by seedsystem
  expect(practitioner).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: expect.stringContaining("AAA Test Practitioner"),
      npi: "1234567894",
    }),
  )
})

test.describe("Practitioner search", () => {
  test("search for a Practitioner by NPI", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "NPI" })
      .fill("1234567894")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by exact name", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "Practitioner" })
      .click()
    await page
      .getByRole("textbox", { name: "Practitioner" })
      .fill("AAA Test Practitioner")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by partial name", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")
    await expect(page.getByRole("button", {name: "Search Providers"})).toBeVisible()

    await page
      .getByRole("textbox", { name: "Practitioner" })
      .click()
    await page
      .getByRole("textbox", { name: "Practitioner" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search Providers" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner and confirm pagination works", async ({ page }) => {
      await page.goto("/search")
      await expect(page).toHaveURL("/search")
      await expect(page.getByText("Search")).toBeVisible()
  
      await page
        .getByRole("textbox", { name: "Practitioner" })
        .click()
      await page
        .getByRole("textbox", { name: "Practitioner" })
        .fill("TEST")
      await page.getByRole("button", { name: "Search" }).click()
      await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
      await expect(page.getByRole("caption")).toContainText(
        "Showing 1 - 10 of 28",
      )
  
      await expect(
        page.locator("[data-testid='searchresults']").getByRole("listitem"),
      ).toHaveCount(10)
  
      await page.getByLabel("Next Page").first().click()
  
      await expect(page).toHaveURL(/page=2/)
      await expect(page.getByRole("caption")).toContainText(
        "Showing 11 - 20 of 28",
      )
      await expect(
        page.locator("[data-testid='searchresults']").getByRole("listitem"),
      ).toHaveCount(10)
  
      await page.getByLabel("Next Page").first().click()
  
      await expect(page).toHaveURL(/page=3/)
      await expect(page.locator("span[role='caption']")).toContainText(
        "Showing 21 - 28 of 28",
      )
      await expect(
        page.locator("[data-testid='searchresults']").getByRole("listitem"),
      ).toHaveCount(8)
    })

    test("search for a Practitioner and view details", async ({ page }) => {
        await page.goto("/search")
        
        await page
          .getByRole("textbox", { name: "NPI" })
          .fill("1234567894")
        await page.getByRole("button", { name: "Search" }).click()
        await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
    
        await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
        await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
        await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
      })
})