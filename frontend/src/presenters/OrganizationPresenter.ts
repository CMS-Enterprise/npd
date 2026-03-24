import type { FHIROrganization } from "../@types/fhir"
import {
  formatAddress,
  formatDetails,
} from "../helpers/formatters"

export class OrganizationPresenter {
  private record: FHIROrganization
  constructor(record: FHIROrganization) { this.record = record}

  get name(): string {
    return this.record.name ?? ""
  }

  get types(): string[] {
    return (
      this.record.extension
        ?.filter(
          (ext) =>
            ext.url ===
            "https://build.fhir.org/organization-definitions.html#Organization.qualification",
        )
        .map((ext) => ext.valueCodeableConcept?.coding?.[0]?.display ?? "") ??
      []
    )
  }

  get npi(): string {
    const npiIdentifier = this.record.identifier?.find(
      (id) =>
        id.system === "http://terminology.hl7.org/NamingSystem/npi" ||
        id.system === "http://hl7.org/fhir/sid/us-npi",
    )
    return npiIdentifier?.value ?? "n/a"
  }

  get address(): string {
    const contact = this.record.contact?.[0]
    if (!contact?.address) return ""
    return formatAddress(contact.address)
  }

  get authorizedOfficial(): string {
    const contact = this.record.contact?.[0]
    return contact?.name?.text ?? ""
  }

  get authorizedPhone(): string {
    const contact = this.record.contact?.[0]
    const phone = contact?.telecom?.find((t) => t.system === "phone")
    return phone?.value ?? ""
  }

  get identifiers() {
    if (!this.record.identifier?.length) return []

    return this.record.identifier.map((identity) => ({
      type: identity.type?.coding?.[0]?.display?.trim() || "Unknown",
      number: identity.value,
      details: identity.period ? formatDetails(identity.period) : "",
    }))
  }
}
