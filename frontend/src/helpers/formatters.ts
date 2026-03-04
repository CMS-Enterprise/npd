import type { Address } from "../@types/fhir/Address"
import type { Period } from "../@types/fhir/Period"

export const formatAddress = (address?: Address): string => {
  if (!address) return ""

  const cityStateZip = [address.city, address.state, address.postalCode]
    .filter(Boolean)
    .join(", ")

  return [address.line, cityStateZip].filter(Boolean).join("\n")
}

export const formatDate = (dateString: string): string => {
  const date = new Date(dateString)

  return date.toLocaleDateString("en-US", {
    month: "long",
    day: "numeric",
    year: "numeric",
  })
}

export const formatIdentifierType = (system: string): string => {
  // prolly will fill up as we get more data
  const systemMap: Record<string, string> = {
    "http://terminology.hl7.org/NamingSystem/npi": "NPI",
  }

  return systemMap[system] || "Other"
}

export const formatDetails = (period: Period): string => {
  const parts: string[] = []

  if (period.start) {
    parts.push(`Issued ${formatDate(period.start)}`)
  }

  if (period.end) {
    parts.push(`Deactivated ${formatDate(period.end)}`)
  }

  return parts.join("; ")
}
