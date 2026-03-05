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
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by exact name", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA Test Practitioner")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner by partial name", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search for a Practitioner and view details", async ({ page }) => {
    await page.goto("/practitioners/search")
    
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })

  test("search for a Practitioner and confirm pagination works", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search practitioners")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("TEST")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
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

test.describe("Practitioner show", () => {
  test("visit a Practitioner page", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })

  test("displays resource type label", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)
    await expect(page.getByText("Practitioner", { exact: true })).toBeVisible()
  })

  test("shows back link when navigating from search", async ({ page }) => {
    await page.goto("/practitioners/search")
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    const backLink = page.getByRole("link", { name: /Back to search results/i })
    await expect(backLink).toBeVisible()
    await expect(backLink).toHaveAttribute("href", /\/practitioners\/search\?/)
  })

  test("back link returns to search with preserved query params", async ({ page }) => {
    await page.goto("/practitioners/search")
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await page.getByRole("link", { name: /Back to search results/i }).click()

    await expect(page).toHaveURL(/\/practitioners\/search/)
    await expect(page).toHaveURL(/query=1234567894/)
  })

  test("does not show back link on direct navigation", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await expect(page.getByTestId("practitioner-name")).toBeVisible()
    await expect(page.getByRole("link", { name: /Back to search results/i })).not.toBeVisible()
  })
})

test.describe("sort Practitioners", () => {
  test("sort dropdown is visible after search", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("First Name (A-Z)")
  })

  test("sort search results by last name", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toContainText("First Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Last Name (A-Z)" }).click()

    await expect(page).toHaveURL(/query=AAA/)
    await expect(page).toHaveURL(/sort=last-name-asc/)
    await expect(sortButton).toContainText("Last Name (A-Z)")
  })
})
