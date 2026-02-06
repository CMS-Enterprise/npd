import type { FHIRPractitioner } from "../@types/fhir";
import {
    formatAddress,
    formatDate
} from "../helpers/formatters"

export class PractitionerPresenter {
    constructor(private record: FHIRPractitioner) {}

    get name(): string {
        const name = this.record.name?.[0]
        return name?.text || "No name available"
      }
    
    get npi(): string | null {
        const npiIdentifier = this.record.identifier?.find(
            (id) => id.system === "http://terminology.hl7.org/NamingSystem/npi"
        )
        return npiIdentifier?.value ?? null
    }

    get address(): string {
        const addr = this.record.address?.[0]
        return addr ? formatAddress(addr) : ""
    }

    get gender(): string | null {
        return this.record.gender ?? null
    }

    get isDeceased(): string {
        return this.record.deceasedBoolean ? "Yes" : "No"
    }

    get isActive(): string {
        return this.record.active ? "Yes" : "No"
    }
    
    get phone(): string | null {
        const phoneTelecom = this.record.telecom?.find((t) => t.system === "phone")
        return phoneTelecom?.value ?? null
    }

    get fax(): string | null {
        const faxTelecom = this.record.telecom?.find((t) => t.system === "fax")
        return faxTelecom?.value ?? null
    }

    get identifiers() {
        if (!this.record.identifier?.length) return []

        return this.record.identifier.map((identity) => ({
            type: identity.type?.coding?.[0]?.display || "Unknown",
            number: identity.value,
            details: identity.period?.start ? `Active, Received ${formatDate(identity.period.start)}` : "",
            system: identity.system,
        }))
    }
}