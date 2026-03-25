import { expect, test } from "@playwright/test"
import { ORGANIZATION } from "../constants"

let organization = ORGANIZATION

// load a known organization record from the API before running tests
test.beforeAll(async ({ request }) => {
  // expects a FhirCollection<FhirOrganization> API response
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

  // it should look like the /fhir/Organization/ record created by seedsystem
  expect(organization).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: "AAA Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Organization search", () => {
  test("search for an Organization by NPI", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("1234567893")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by exact name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA Test Org")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for an Organization by partial name", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Organization search")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("AAA")
    await page.getByRole("button", { name: "Search" }).click()
    await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  })

  test("search for a Organization and confirm pagination works", async ({ page }) => {
    await page.goto("/organizations/search")
    await expect(page).toHaveURL("/organizations/search")
    await expect(page.getByText("Search organizations")).toBeVisible()

    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .click()
    await page
      .getByRole("textbox", { name: "Name or NPI" })
      .fill("TEST")
    await page.getByRole("button", { name: "Search" }).click()
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

test.describe("Organization show", () => {
  test("visit an Organization page", async ({ page }) => {
    await page.goto("/organizations/search")
    
    await page.getByRole("textbox", { name: "Name or NPI" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    await expect(page.getByTestId("organization-name")).toContainText(organization.name)
    await expect(page.getByTestId("organization-npi")).toContainText(`NPI: ${organization.npi}`)
  })

  test("displays resource type label", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)
    await expect(page.getByText("Organization", { exact: true })).toBeVisible()
  })

  test("shows back link when navigating from search", async ({ page }) => {
    await page.goto("/organizations/search")
    await page.getByRole("textbox", { name: "Name or NPI" }).fill(organization.name)
    await page.getByRole("button", { name: "Search" }).click()
    await page.getByRole("link", { name: organization.name }).click()

    await expect(page).toHaveURL(`/organizations/${organization.id}`)
    const backLink = page.getByRole("link", { name: /Back to search results/i })
    await expect(backLink).toBeVisible()
    await expect(backLink).toHaveAttribute("href", /\/organizations\/search\?/)
  })

  test("back link returns to search with preserved query params", async ({ page }) => {
    await page.goto("/organizations/search")
    await page.getByRole("textbox", { name: "Name or NPI" }).fill(organization.name)
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
})

test.describe("sort Organizations", () => {
  test("sort dropdown is visible after search", async ({ page }) => {
    await page.goto("/organizations/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("Test")
    await page.getByRole("button", { name: "Search" }).click()

    await expect(page.locator("[data-testid='searchresults']").getByRole("listitem").first()).toBeVisible()

    const sortButton = page.locator(".ds-c-dropdown__button")
    await expect(sortButton).toBeVisible()
    await expect(sortButton).toContainText("Name (A-Z)")
  })

  test("sort search results by name descending", async ({ page }) => {
    await page.goto("/organizations/search")

    await page.getByRole("textbox", { name: "Name or NPI" }).fill("Test")
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
  await page.goto("/organizations/search")
  
  await page.getByRole("textbox", { name: "Name or NPI" }).fill("1234567893")
  await page.getByRole("button", { name: "Search" }).click()
  
  await expect(page.getByRole("link", { name: "AAA Test Org" })).toBeVisible()
  await expect(page.getByRole("link", { name: "BBB Other ID Org" })).not.toBeVisible()
})


test.describe("Organization feedback", () => {
  test("report an issue button opens the feedback dialog", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()
    await expect(dialog.getByText(organization.name)).toBeVisible()
  })

  test("submit is disabled when no issues are selected", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeDisabled()
  })

  test("submit is enabled after selecting an issue", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("checkbox", { name: /Practice location/i }).check()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()
  })

  test("selecting 'Other' requires details text", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("checkbox", { name: /Other/i }).check()

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeDisabled()

    await dialog
      .getByRole("textbox", { name: /details/i })
      .fill("Additional details about the issue")

    await expect(dialog.getByRole("button", { name: "Submit" })).toBeEnabled()
  })

  test("cancel closes the feedback dialog", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await dialog.getByRole("button", { name: "Cancel" }).click()

    await expect(dialog).not.toBeVisible()
  })

  test("submitting feedback shows success message", async ({ page }) => {
    await page.goto(`/organizations/${organization.id}`)

    await page.getByRole("button", { name: "Report an issue" }).click()

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

    await page.getByRole("button", { name: "Report an issue" }).click()

    const dialog = page.getByRole("dialog")
    await expect(dialog).toBeVisible()

    await expect(dialog.getByText(organization.name)).toBeVisible()
  })
})
