import type { FHIRLocation, FHIRReference } from "../@types/fhir"
import type { OrganizationDetails, PractitionerDetailsType } from "../state/requests/practitioners"
import {
  formatAddress,
  formatDetails,
  formatIdentifierType,
} from "../helpers/formatters"
import type { LogicalIdOfThisArtifact } from "../@types/fhir/Endpoint"

export class PractitionerPresenter {
  private record: PractitionerDetailsType
  constructor(record: PractitionerDetailsType) {this.record = record}

  get name(): string {
    const name = this.record.name?.[0]
    return name?.text || "No name available"
  }

  get npi(): string | null {
    const npiIdentifier = this.record.identifier?.find(
      (id) => id.system === "http://terminology.hl7.org/NamingSystem/npi",
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
      details: identity.period ? formatDetails(identity.period) : "",
      system: formatIdentifierType(identity.system as string) || "Unknown",
    }))
  }

  get taxonomy() {
    if (!this.record.qualification?.length) return []

    return this.record.qualification.map((taxonomy) => ({
      state: taxonomy.identifier?.[0]?.assigner?.display ?? "",
      licenseNumber: taxonomy.identifier?.[0]?.value ?? "",
      display: taxonomy.code?.coding?.[0]?.display ?? "Unknown",
      nuccCode: taxonomy.code?.coding?.[0]?.code ?? "Unknown",
    }))
  }

  get organizations() {
    if (!this.record.practitionerRoleData?.results?.entry?.length) return []
    const organizationDetailData: OrganizationDetails = {};
    this.record.practitionerRoleData.results.entry.forEach((role) => {
      const organizationId = role?.resource.organization.reference.split('/').pop();
      const locationId = role?.resource.location[0].reference.split('/').pop();
      const endpointIds = role?.resource.endpoint?.map((endpoint: FHIRReference) => { return endpoint.reference.split('/').pop()});
      if (organizationId && Object.keys(organizationDetailData).includes(organizationId)) {
        let existingEndpointIds: Array<string | undefined> = organizationDetailData[organizationId].endpoints?.map((endpoint) => endpoint?.id )
        endpointIds?.forEach( (endpointId) => {
          if (endpointId && !existingEndpointIds.includes(endpointId)) {
            organizationDetailData[organizationId].endpoints.push(this.record.endpointData[endpointId])
          }
        })
        let existingLocationIds: Array<LogicalIdOfThisArtifact | undefined> = organizationDetailData[organizationId].locations.map((location: FHIRLocation) => location.id)
        if (locationId && !existingLocationIds.includes(locationId)) {
          organizationDetailData[organizationId].locations.push(this.record.locationData[locationId])
        }
      }
      else {
        if (organizationId && locationId){
          organizationDetailData[organizationId] = {
            organization: this.record.organizationData[organizationId],
            endpoints: endpointIds?.map((endpointId) => {
              if (endpointId) {
                return this.record.endpointData[endpointId]
              }
              else {
                return null
              }
            }) ?? [],
            locations: [this.record.locationData[locationId]],
            roleDetails: role?.resource
          };
        }
      }
  })
  return {
    ...organizationDetailData
  }
  }
}