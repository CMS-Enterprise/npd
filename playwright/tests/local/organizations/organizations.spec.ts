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

test.describe("Organization show", () => {
  test("visit an Organization page", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: "Organization" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    await expect(page.getByTestId("organization-name")).toContainText(organization.name)
    await expect(page.getByTestId("organization-npi")).toContainText(`NPI: ${organization.npi}`)
    await expect(page.getByRole("heading", { name: "Basic Information" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
  })

  test.fixme("displays resource type label", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)
    await expect(page.getByText("Organization", { exact: true })).toBeVisible()
  })

  test.fixme("shows back link when navigating from search", async ({ page }) => {
    await page.goto("/organizations/search")
    await page.getByRole("textbox", { name: "Organization" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    const backLink = page.getByRole("link", { name: /Back to search results/i })
    await expect(backLink).toBeVisible()
    await expect(backLink).toHaveAttribute("href", /\/organizations\/search\?/)
  })

  test.fixme("back link returns to search with preserved query params", async ({ page }) => {
    await page.goto("/organizations/search")
    await page.getByRole("textbox", { name: "Organization" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    await page.getByRole("link", { name: /Back to search results/i }).click()

    await expect(page).toHaveURL(/\/organizations\/search/)
    await expect(page).toHaveURL(/query=AAA/)
  })

  test("does not show back link on direct navigation", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await expect(page.getByTestId("organization-name")).toBeVisible()
    await expect(page.getByRole("link", { name: /Back to search results/i })).not.toBeVisible()
  })

  test("View an organization with no practitioner relationships", async ({page}) => {
    await page.goto(`/organizations/98d3090b-0982-495f-9eb9-4e79523d2ba2`)

    await expect(page.getByTestId("organization-name")).toContainText("BBB Other ID Org")
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
    await expect(page.getByText("No practitioner information available")).toHaveCount(0)
    await expect(page.getByRole("heading", { name: "Practitioner(s)" })).toHaveCount(0)
  })
  test("View an organization with one practitioner relationship", async ({page}) => {
    await page.goto(`/organizations/eca64970-4833-4c64-b3fa-d583f9af7fcc`)

    await expect(page.getByTestId("organization-name")).toContainText("Organization ABC")
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
    await expect(page.getByText("No practitioner information available")).toHaveCount(0)
    await expect(page.getByRole("heading", { name: "Practitioner(s)" })).toHaveCount(0)
  })
  test("View an organization with multiple practitioner relationships", async ({page}) => {
    await page.goto(`/organizations/0c1f8f84-0502-4444-b636-8fee4ab76e32`)

    await expect(page.getByTestId("organization-name")).toContainText("Organization ABC")
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
    await expect(page.getByText("No practitioner information available")).toHaveCount(0)
    await expect(page.getByRole("heading", { name: "Practitioner(s)" })).toHaveCount(0)
  })
  test("View an organization with a location but no endpoints", async ({page}) => {
    await page.goto(`/organizations/53202937-ac54-4c71-b3dc-9a773bd51fc2`)

    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
    await expect(page.getByText("No endpoint information available.")).toBeVisible()
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByText("No practice location information available.")).toHaveCount(0)
  })
  test("View an organization with no locations", async ({page}) => {
    await page.goto(`/organizations/8450a7cd-c919-47ee-9c59-bc17538231ef`)

    await expect(page.getByRole("heading", { name: "Data Exchange Endpoints" })).toBeVisible()
    await expect(page.getByText("No endpoint information available.")).toBeVisible()
    await expect(page.getByRole("heading", { name: "Practice Locations" })).toBeVisible()
    await expect(page.getByText("No practice location information available.")).toBeVisible()
  })
})


test.describe("sort Organizations", () => {
  test.fixme("sort dropdown is visible after search", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: "Organization" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("Name (A-Z)")
  })

  test.fixme("sort search results by name descending", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: "Organization" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toContainText("Name (A-Z)")

    await sortButton.click()
    await expect(page.locator("[role='listbox']")).toBeVisible()
    await page.getByRole("option", { name: "Name (Z-A)" }).click()

    await expect(page).toHaveURL(/query=Test/)
    await expect(page).toHaveURL(/sort=name-desc/)
    await expect(sortButton).toContainText("Name (Z-A)")
  })
})

test("search by NPI excludes organizations with matching other_id", async ({ page }) => {
  await page.goto("/search")
  
  await page.getByRole("textbox", { name: "NPI" }).fill("1234567893")
  await page.getByRole("button", { name: "Search" }).click()
  
  await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  await expect(page.getByRole("link", { name: "BBB Other ID Org" })).not.toBeVisible()
})

test.describe("Organization feedback", () => {
  test("Report Issue with This Record button opens the feedback dialog", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await expect(dialog.getByText(organization.name)).toBeVisible()
  })

  test("submitting with no issues selected shows error", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()

    const captcha = dialog.getByRole("checkbox", { name: /I'm not a robot/i })
    await captcha.click()
    
    await expect(
      dialog.getByRole("checkbox", { name: /Verified/i })
    ).toBeChecked({ timeout: 10000 })

    await dialog.getByRole("button", { name: "Submit" }).click()

    const errorAlert = dialog.getByRole('alert', { name: 'Alert: This form contains the' })
    await expect(errorAlert).toBeVisible()
    await expect(errorAlert.getByText(/select at least one issue/i)).toBeVisible()
  })

  test("submit is enabled regardless of selection state", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    // enabled with nothing selected
    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()

    // still enabled after selecting an issue
    await dialog.getByRole("checkbox", { name: /Practice location/i }).check()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()
  })

  test("selecting 'Other' and submitting without details shows error", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

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
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("button", { name: "Close modal dialog" }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("submitting feedback shows success message", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

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

  test("feedback form shows organization name", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report Issue with This Record" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByText(organization.name)).toBeVisible()
  })
})
