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

test.describe("Practitioner show", () => {
  test("visit a Practitioner page", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    await expect(page.getByTestId("practitioner-name")).toContainText(practitioner.name)
    await expect(page.getByText(practitioner.npi)).toBeVisible()
    await expect(page.getByText("No organization relationship found")).toBeVisible()
  })

  test("view organization relationship information - single organization", async ({ page }) => {
    await page.goto("/practitioners/6846963d-7814-4c70-ae3d-8a8419a7c9c6")

    await expect(page).toHaveURL("/practitioners/6846963d-7814-4c70-ae3d-8a8419a7c9c6")
    await expect(page.getByText("1000000001")).toBeVisible()
    await expect(page.getByText("No organization relationship found")).not.toBeVisible()
    await expect(page.getByText("1000000002")).toBeVisible()
    await expect(page.getByRole("heading", { name: "Locations" })).toBeVisible()
    await expect(page.getByText("No location information available")).not.toBeVisible()
    await expect(page.getByText("Endpoint(s)")).toBeVisible()
    await expect(page.getByText("No endpoint information available")).not.toBeVisible()
  })

  test("view organization relationship information - single organization, no endpoints", async ({ page }) => {
    await page.goto("/practitioners/f1579a55-b5e1-4717-988d-6e014acbe348")

    await expect(page).toHaveURL("/practitioners/f1579a55-b5e1-4717-988d-6e014acbe348")
    await expect(page.getByText("1000000011")).toBeVisible()
    await expect(page.getByText("No organization relationship found")).not.toBeVisible()
    await expect(page.getByText("1000000012")).toBeVisible()
    //await expect (page.getByRole('link', { name: 'Organization ABC (NPI: 1000000012)' })).toHaveAttribute("href", "/organizations/893149b6-34de-4030-a2fa-89cc02baccbe")
    await expect(page.getByRole("heading", { name: "Location(s)" })).toBeVisible()
    await expect(page.getByText("No location information available")).not.toBeVisible()
    await expect(page.getByText("Endpoint(s)")).toBeVisible()
    await expect(page.getByText("No endpoint information available")).toBeVisible()
  })
  

  test("view organization relationship information - multiple organizations", async ({ page }) => {
    await page.goto("/practitioners/1d58f0f5-2075-4e9f-b7a5-2245e74f6a16")

    await expect(page).toHaveURL("/practitioners/1d58f0f5-2075-4e9f-b7a5-2245e74f6a16")
    await expect(page.getByText("1000000003")).toBeVisible()
    await expect(page.getByText("No organization relationship found")).not.toBeVisible()
    await expect(page.getByText("NPI: 1000000004")).toBeVisible()
    await expect(page.getByText("NPI: 1000000005")).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Location(s)' }).first()).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Location(s)' }).nth(1)).toBeVisible()
    await expect(page.getByText("No location information available")).not.toBeVisible()
    await expect(page.getByRole('heading', { name: 'Endpoint(s)' }).first()).toBeVisible()
    await expect(page.getByRole('heading', { name: 'Endpoint(s)' }).nth(1)).toBeVisible()
    await expect(page.getByText("No endpoint information available")).not.toBeVisible()
  })

  test.fixme("displays resource type label", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)
    await expect(page.getByText("Practitioner", { exact: true })).toBeVisible()
  })

  test.fixme("shows back link when navigating from search", async ({ page }) => {
    await page.goto("/practitioners/search")
    await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567894")
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()

    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
    const backLink = page.getByRole("link", { name: /Back to search results/i })
    await expect(backLink).toBeVisible()
    await expect(backLink).toHaveAttribute("href", /\/practitioners\/search\?/)
  })

  test.fixme("back link returns to search with preserved query params", async ({ page }) => {
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
  test.fixme("sort dropdown is visible after search", async ({ page }) => {
    await page.goto("/practitioners/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("First Name (A-Z)")
  })

  test.fixme("sort search results by last name", async ({ page }) => {
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

test.describe("Practitioner feedback", () => {
  test("Report issue with this record button opens the feedback dialog", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await expect(dialog.getByText(practitioner.name)).toBeVisible()
  })

  test("submitting with no issues selected shows error", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()

    const captcha = dialog.getByRole("checkbox", { name: /I'm not a robot/i })
    await captcha.click()
    
    await expect(
      dialog.getByRole("checkbox", { name: /Verified/i })
    ).toBeChecked({ timeout: 10000 })

    await dialog.getByRole("button", { name: "Submit" }).click()

    const errorAlert = dialog.getByRole("alert", { name: /this form contains the/i })
    await expect(errorAlert).toBeVisible()
    await expect(errorAlert.getByText(/select at least one issue/i)).toBeVisible()
  })

  test("submit is enabled regardless of selection state", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()

    await dialog.getByRole("checkbox", { name: /Practice location/i }).check()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()
  })

  test("selecting 'Other' and submitting without details shows error", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("checkbox", { name: /Other/i }).check()

    const captcha = dialog.getByRole("checkbox", { name: /I'm not a robot/i })
    await captcha.click()
    
    await expect(
      dialog.getByRole("checkbox", { name: /Verified/i })
    ).toBeChecked({ timeout: 10000 })

    await dialog.getByRole("button", { name: "Submit" }).click()

    const errorAlert = dialog.getByRole("alert", { name: /this form contains the/i })
    await expect(errorAlert).toBeVisible()

    await dialog.getByRole("textbox", { name: /details/i }).fill("Additional details about the issue")

    await dialog.getByRole("button", { name: "Submit" }).click()

    await expect(errorAlert).not.toBeVisible()
  })

  test("xmark closes the feedback dialog", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("button", { name: "Close modal dialog" }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("submitting feedback shows success message", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("checkbox", { name: /Practice location/i }).check()

    const captcha = dialog.getByRole("checkbox", { name: /I'm not a robot/i })
    await captcha.click()
    
    await expect(
      dialog.getByRole("checkbox", { name: /Verified/i })
    ).toBeChecked({ timeout: 10000 })

    await dialog.getByRole("button", { name: "Submit" }).click()

    await expect(dialog.getByText(/success/i)).toBeVisible()
    await dialog.getByRole("button", { name: "Close", exact: true }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("feedback form shows practitioner name", async ({ page }) => {
    await page.goto(`/practitioners/${practitioner.id}`)

    await page.getByRole("button", { name: "Report issue with this record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByText(practitioner.name)).toBeVisible()
  })
})
