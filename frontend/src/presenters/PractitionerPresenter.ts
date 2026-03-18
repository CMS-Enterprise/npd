import type { PractitionerDetailsType } from "../state/requests/practitioners"
import {
  formatAddress,
  formatDetails,
  formatIdentifierType,
} from "../helpers/formatters"

export class PractitionerPresenter {
  record: PractitionerDetailsType;
  constructor(record: PractitionerDetailsType ) { this.record = record; }

  get name(): string {
    const name = this.record.practitioner?.name?.[0]
    return name?.text || "No name available"
  }

  get npi(): string | null {
    const npiIdentifier = this.record.practitioner?.identifier?.find(
      (id) => id.system === "http://terminology.hl7.org/NamingSystem/npi",
    )
    return npiIdentifier?.value ?? null
  }

  get address(): string {
    const addr = this.record.practitioner?.address?.[0]
    return addr ? formatAddress(addr) : ""
  }

  get gender(): string | null {
    return this.record.practitioner?.gender ?? null
  }

  get isDeceased(): string {
    return this.record.practitioner?.deceasedBoolean ? "Yes" : "No"
  }

  get isActive(): string {
    return this.record.practitioner?.active ? "Yes" : "No"
  }

  get phone(): string | null {
    const phoneTelecom = this.record.practitioner?.telecom?.find((t) => t.system === "phone")
    return phoneTelecom?.value ?? null
  }

  get fax(): string | null {
    const faxTelecom = this.record.practitioner?.telecom?.find((t) => t.system === "fax")
    return faxTelecom?.value ?? null
  }

  get identifiers() {
    if (!this.record.practitioner?.identifier?.length) return []

    return this.record.practitioner?.identifier.map((identity) => ({
      type: identity.type?.coding?.[0]?.display || "Unknown",
      number: identity.value,
      details: identity.period ? formatDetails(identity.period) : "",
      system: formatIdentifierType(identity.system as string) || "Unknown",
    }))
  }

  get taxonomy() {
    if (!this.record.practitioner?.qualification?.length) return []

    return this.record.practitioner?.qualification.map((taxonomy) => ({
      state: "", // we arent capturing this currently, we could use the state they're from?
      licenseNumber: taxonomy.code?.coding?.[0]?.code || "Unknown",
      displayCode: taxonomy.code?.coding?.[0]?.display || "Unknown",
    }))
  }
}
