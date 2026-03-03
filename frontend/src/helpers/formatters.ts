import type { Address } from "../@types/fhir/Address"
import type { Period } from "../@types/fhir/Period"

export const formatAddress = (
  address?: Address,
  { singleLine = false }: { singleLine?: boolean } = {},
): string => {
  if (!address) return ""

  const street = address.line?.filter(Boolean).join(", ") ?? ""
  const cityState = [address.city, address.state].filter(Boolean).join(", ")
  const cityStateZip = [cityState, address.postalCode].filter(Boolean).join(" ")

  const separator = singleLine ? ", " : "\n"
  return [street, cityStateZip].filter(Boolean).join(separator)
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
