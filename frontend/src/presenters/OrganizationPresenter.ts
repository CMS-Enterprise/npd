import type { FHIROrganization } from "../@types/fhir"
import {
  formatAddress,
  formatDetails,
  formatOtherIdentifierType,
} from "../helpers/formatters"
import type { OrganizationDetailsType } from "../state/requests/organizations"

export class OrganizationPresenter {
  private record: FHIROrganization
  constructor(record: FHIROrganization) { this.record = record }

  get name(): string {
    return this.record.name ?? ""
  }

  get otherNames(): Array<string | null> {
    return this.record.alias ?? []
  }

  get types() {
    return (
      this.record.extension
        ?.filter(
          (ext) =>
            ext.url ===
            "https://build.fhir.org/organization-definitions.html#Organization.qualification",
        )
        .map((ext) => (
          {
            display: ext.valueCodeableConcept?.coding?.[0]?.display ?? "",
            nuccCode: ext.valueCodeableConcept?.coding?.[0]?.code ?? "" 
          })) ??
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
      type: formatOtherIdentifierType(identity.type?.coding?.[0]?.code),
      number: identity.value,
      details: identity.period || identity.assigner ? formatDetails(identity.period, identity.assigner?.display) : "",
    }))
  }

  get parent() {
    return this.record.partOf?.display
  }

  }

export class FullOrganizationPresenter {
  private record: OrganizationDetailsType
  constructor(record: OrganizationDetailsType) { this.record = record }

  get practitioners() {
    if (!this.record.practitionerData?.length) return []

    return this.record.practitionerData.map((practitioner) => ({
      id: practitioner?.id,
      name: practitioner?.name,
      //taxonomy: practitioner?.qualification?.[0]?.code?.coding?.[0]?.display ?? "Unknown",
    }))
  }

  get locations() {
    if (!this.record.locationData?.results.entry.length) return []

    return this.record.locationData.results.entry.map((location) => ({
      id: location?.resource.id,
      name: location?.resource.name,
      address: formatAddress(location?.resource.address, false),
      contact: location?.resource.telecom
    }))
  }

  get endpoints() {
    if (!this.record.endpointData?.length || this.record.endpointData[0] == undefined) return []

    return this.record.endpointData.map((endpoint) => ({
      id: endpoint?.id,
      address: endpoint?.address,
      connectionType: endpoint?.connectionType.display
    }))
  }

  }