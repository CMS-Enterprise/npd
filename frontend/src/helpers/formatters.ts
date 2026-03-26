import type { Address } from "../@types/fhir/Address"
import type { Period } from "../@types/fhir/Period"
import type { FHIRReference } from "../@types/fhir"

export const formatAddress = (address?: Address, multiLine: boolean = true): string => {
  if (!address) return ""

  const street = address.line?.filter(Boolean).join(multiLine ? "\n" : " ") ?? ""
  const cityState = [address.city, address.state].filter(Boolean).join(", ")
  const cityStateZip = [cityState, address.postalCode].filter(Boolean).join(" ")

  if (multiLine) {
    return [street, cityStateZip].filter(Boolean).join("\n")
  }
  else {
    return [street, cityStateZip].filter(Boolean).join(", ")
  }
}

export const formatOtherIdentifierType = (otherIdentifierType: string | undefined | null): string => {
  switch (otherIdentifierType) {
    case "NPI":
      return "National Provider Identifier"
    case "UPIN":
      return "Medicare"
    case "MCR":
      return "Medicare"
    case "MCD":
      return "Medicaid"
    case "PPIN":
      return "Medicare"
    default:
      return "Other"
  }
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)

  return date.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  })
}

export const formatDetails = (period: Period | undefined, assigner: string | null | undefined): string => {
  const parts: string[] = []

  if (assigner) {
    parts.push(`Issuer: ${assigner}`)
  }

  if (period?.start) {
    parts.push(`Issued ${formatDate(period.start)}`)
  }

  if (period?.end) {
    parts.push(`Deactivated ${formatDate(period.end)}`)
  }

  return parts.join("; ")
}
