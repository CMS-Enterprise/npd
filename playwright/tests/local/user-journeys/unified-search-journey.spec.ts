import { expect, test } from "@playwright/test"
import { PRACTITIONER, ORGANIZATION } from "../constants"

let practitioner = PRACTITIONER
let organization = ORGANIZATION

test.beforeAll(async ({ request }) => {
  const [practResp, orgResp] = await Promise.all([
    request.get("/fhir/Practitioner/?identifier=NPI|1234567894"),
    request.get("/fhir/Organization/?identifier=1234567893"),
  ])

  const practPayload = await practResp.json()
  const practResource = practPayload.results.entry[0].resource
  const nameRecord = practResource.name?.[0]
  practitioner = {
    id: practResource.id,
    name:
      nameRecord?.text ||
      `${nameRecord?.given?.[0] || ""} ${nameRecord?.family || ""}`.trim(),
    npi:
      practResource.identifier?.find(
        (i: { system?: string }) =>
          i.system === "http://hl7.org/fhir/sid/us-npi" ||
          i.system === "http://terminology.hl7.org/NamingSystem/npi",
      )?.value || practResource.identifier?.[0]?.value,
  }

  const orgPayload = await orgResp.json()
  const orgResource = orgPayload.results.entry[0].resource
  organization = {
    id: orgResource.id,
    name: orgResource.name,
    npi: orgResource.identifier[0].value,
  }

  expect(practitioner).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: expect.stringContaining("AAA Test Practitioner"),
      npi: "1234567894",
    }),
  )
  expect(organization).toMatchObject(
    expect.objectContaining({
      id: expect.stringMatching(/[\d-]+/),
      name: "AAA Test Org",
      npi: "1234567893",
    }),
  )
})

test.describe("Unified Search Journey", () => {
  test("initial state: form visible, search button disabled", async ({ page }) => {
    await page.goto("/search")
    await expect(page).toHaveURL("/search")

    await expect(page.getByRole("textbox", { name: /provider name/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /organization/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /npi number/i })).toBeVisible()
    await expect(page.getByRole("textbox", { name: /location/i })).toBeVisible()
    await expect(page.getByRole("button", { name: /search providers/i })).toBeDisabled()
  })

  test("search by provider name returns results", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /provider name/i }).fill("AAA Test Practitioner")
    await page.getByRole("button", { name: /search providers/i }).click()

    await expect(page.getByTestId("searchresults")).toBeVisible()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()
  })

  test("search by NPI navigates to practitioner detail", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /npi number/i }).fill("1234567894")
    await page.getByRole("button", { name: /search providers/i }).click()

    await expect(page.getByTestId("searchresults")).toBeVisible()
    await expect(page.getByRole("link", { name: /AAA Test Practitioner/i })).toBeVisible()

    await page.getByRole("link", { name: /AAA Test Practitioner/i }).click()
    await expect(page).toHaveURL(`/practitioners/${practitioner.id}`)
  })

  test("search by organization name returns results", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /organization/i }).fill("AAA Test Org")
    await page.getByRole("button", { name: /search providers/i }).click()

    await expect(page.getByTestId("searchresults")).toBeVisible()
    await expect(page.getByRole("link", { name: /AAA Test Org/i })).toBeVisible()
  })

  test("location-only input shows hint and keeps button disabled", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /location/i }).fill("CA")
    await expect(page.getByRole("button", { name: /search providers/i })).toBeDisabled()
    await expect(page.getByText(/please also enter a provider name/i)).toBeVisible()
  })

  test("clear button resets the form", async ({ page }) => {
    await page.goto("/search")

    await page.getByRole("textbox", { name: /provider name/i }).fill("AAA Test Practitioner")
    await expect(page.getByRole("button", { name: /search providers/i })).not.toBeDisabled()

    await page.getByRole("button", { name: /clear/i }).click()
    await expect(page.getByRole("textbox", { name: /provider name/i })).toHaveValue("")
    await expect(page.getByRole("button", { name: /search providers/i })).toBeDisabled()
  })
})
