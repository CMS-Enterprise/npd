import { expect, test } from "@playwright/test"
import { PRACTITIONER } from "../constants"

let practitioner = PRACTITIONER

// load a known practitioner record from the API before running tests
test.beforeAll(async ({ request }) => {
  const response = await request.get(
    "/fhir/Practitioner/?identifier=NPI|1234567894",
  )
  const payload = await response.json()
  const resource = payload.results.entry[0].resource

  const nameRecord = resource.name?.[0]
  const name = nameRecord?.text || 
    `${nameRecord?.given?.[0] || ""} ${nameRecord?.family || ""}`.trim()

  practitioner = {
    id: resource.id,
    name: name,
    npi: resource.identifier?.find(
      (i: { system?: string }) => 
        i.system === "http://hl7.org/fhir/sid/us-npi" || 
        i.system === "http://terminology.hl7.org/NamingSystem/npi"
    )?.value || resource.identifier?.[0]?.value,
  }

  expect(practitioner).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: expect.stringContaining("AAA Test Practitioner"),
      npi: "1234567894",
    }),
  )
})

test.describe("Practitioner Journey", () => {
  test("landing -> search hub -> practitioner search -> detail view", async ({ page }) => {
    await page.goto("/practitioners/search")
    await expect(page).toHaveURL("/practitioners/search")
    await expect(page.getByText("Search Practitioners")).toBeVisible()

    // then, perform search by NPI
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()

    // then, confirm search results appear
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()

    // then, click on practitioner to view details
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    // finally, confirm detail page content
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByTestId("practitioner-npi")).toContainText(`NPI: ${practitioner.npi}`)
  })

  test("landing -> last page -> practitioner detail", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("TEST")
    await page.getByRole("button", { name: "Search" }).click()
  
    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toContainText("First Name (A-Z)")
    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "First Name (Z-A)" }).click()
    await expect(sortButton).toContainText("First Name (Z-A)")
  
    await page.getByLabel("Next Page").first().click()
    await expect(page).toHaveURL(/page=2/)
  
    await page.getByLabel("Next Page").first().click()
    await expect(page).toHaveURL(/page=3/)
  
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
  
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
  })

  test("practitioner journey with partial name search", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
  })

  test("practitioner journey with sorting functionality", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("First Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Last Name (A-Z)" }).click()

    await expect(page).toHaveURL(/sort=last-name-asc/)
    await expect(sortButton).toContainText("Last Name (A-Z)")

    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
  })

  test("search -> detail -> report feedback", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /npi number/i }).fill("1234567894")
    await page.getByRole("button", { name: /search providers/i }).click()

    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)

    // open feedback dialog
    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    // confirm practitioner name is shown in the form
    await expect(dialog.getByText(practitioner.name)).toBeVisible()

    // check issue type
    await dialog.getByRole("checkbox", { name: /Practice location/i }).check()
    await dialog.getByRole("textbox", { name: /details/i }).fill("Address is outdated")

    const captcha = dialog.getByRole("checkbox", { name: /I'm not a robot/i })
    await captcha.click()
    await expect(
      dialog.getByRole("checkbox", { name: /Verified/i })
    ).toBeChecked({ timeout: 10000 })

    // fill details after captcha is verified
    await dialog.getByRole("textbox", { name: /details/i }).fill("Address is outdated")

    await dialog.getByRole("button", { name: "Submit" }).click()

    // confirm success message
    await expect(dialog.getByText(/Submission sent/i)).toBeVisible()

    // close the dialog
    await dialog.getByRole("button", { name: "Close", exact: true }).click()
    await expect(dialog).not.toBeVisible()

    // confirm we're still on the detail page
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
  })
})