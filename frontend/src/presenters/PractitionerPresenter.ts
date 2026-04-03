import type { FHIRPractitioner, FHIRReference } from "../@types/fhir"
import type {
  OrganizationDetails,
  PractitionerDetailsType,
} from "../state/requests/practitioners"
import {
  formatAddress,
  formatDetails,
  formatOtherIdentifierType,
} from "../helpers/formatters"
import type { LogicalIdOfThisArtifact } from "../@types/fhir/Endpoint"

export class PractitionerPresenter {
  private record: FHIRPractitioner
  constructor(record: FHIRPractitioner) {
    this.record = record
  }

  get names(): Array<string | undefined | null> {
    const names = this.record.name
    return names?.map((name) => name.text) || []
  }

  get npi(): string | null {
    return this.findNpiIdentifier(this.record.identifier)?.value ?? null
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

    return this.record.identifier
      .filter(
        (identity) => identity.value && !this.isNpiIdentifier(identity.system),
      )
      .map((identity) => ({
        type: formatOtherIdentifierType(identity.type?.coding?.[0]?.code),
        number: identity.value,
        details:
          identity.period || identity.assigner
            ? formatDetails(identity.period, identity.assigner?.display)
            : "",
      }))
  }

  get taxonomy() {
    if (!this.record.qualification?.length) return []

    return this.record.qualification
      .map((taxonomy) => ({
        state: taxonomy.identifier?.[0]?.assigner?.display ?? "",
        licenseNumber: taxonomy.identifier?.[0]?.value ?? "",
        display: taxonomy.code?.coding?.[0]?.display ?? "",
        nuccCode: taxonomy.code?.coding?.[0]?.code ?? "",
      }))
      .filter((taxonomy) => taxonomy.display || taxonomy.nuccCode)
  }

  get primaryTaxonomy(): string | null {
    return this.taxonomy[0]?.display ?? null
  }

  private isNpiIdentifier(system: string | undefined): boolean {
    return (
      system === "http://terminology.hl7.org/NamingSystem/npi" ||
      system === "http://hl7.org/fhir/sid/us-npi"
    )
  }

  private findNpiIdentifier(identifiers: FHIRPractitioner["identifier"]) {
    return identifiers?.find((id) => this.isNpiIdentifier(id.system))
  }
}

export class FullPractitionerPresenter {
  private record: PractitionerDetailsType
  constructor(record: PractitionerDetailsType) {
    this.record = record
  }
  get organizations() {
    if (!this.record.practitionerRoleData?.results?.entry?.length) return []
    const organizationDetailData: OrganizationDetails = {}
    this.record.practitionerRoleData.results.entry.forEach((role) => {
      const organizationId = role?.resource.organization.reference
        .split("/")
        .pop()
      const locationId = role?.resource.location[0].reference.split("/").pop()
      const endpointIds = role?.resource.endpoint?.map(
        (endpoint: FHIRReference) => {
          return endpoint.reference.split("/").pop()
        },
      )
      if (
        organizationId &&
        Object.keys(organizationDetailData).includes(organizationId)
      ) {
        const existingEndpointIds: Array<string | undefined> =
          organizationDetailData[organizationId].endpoints?.map(
            (endpoint) => endpoint?.id,
          )
        endpointIds?.forEach((endpointId) => {
          if (endpointId && !existingEndpointIds.includes(endpointId)) {
            const endpoint = this.record.endpointData[endpointId]
            if (endpoint) {
              const endpointRecord = {
                id: endpoint.id,
                address: endpoint.address,
                connectionType: endpoint.connectionType.display,
              }
              organizationDetailData[organizationId].endpoints.push(
                endpointRecord,
              )
            }
          }
        })
        const existingLocationIds: Array<LogicalIdOfThisArtifact | undefined> =
          organizationDetailData[organizationId].locations.map(
            (location) => location.id,
          )
        if (locationId && !existingLocationIds.includes(locationId)) {
          const loc = this.record.locationData[locationId]
          if (loc) {
            const locRecord = {
              id: loc.id,
              name: loc.name,
              address: formatAddress(loc.address, false),
              contact: loc.telecom,
            }
            organizationDetailData[organizationId].locations.push(locRecord)
          }
        }
      } else {
        if (organizationId && locationId) {
          const loc = this.record.locationData[locationId]
          const organization = this.record.organizationData[organizationId]
          if (organization && loc) {
            const locRecord = {
              id: loc.id,
              name: loc.name,
              address: formatAddress(loc.address, false),
              contact: loc.telecom,
            }
            organizationDetailData[organizationId] = {
              organization,
              endpoints:
                endpointIds?.map((endpointId) => {
                  if (endpointId) {
                    const endpoint = this.record.endpointData[endpointId]
                    if (endpoint) {
                      const endpointRecord = {
                        id: endpoint.id,
                        address: endpoint.address,
                        connectionType: endpoint.connectionType.display,
                      }
                      return endpointRecord
                    }
                  }
                }) ?? [],
              locations: [locRecord],
              roleDetails: role?.resource,
            }
          }
        }
      }
    })

    return {
      ...organizationDetailData,
    }
  }

  get organizationCards() {
    return Object.entries(this.organizations).map(([id, obj]) => {
      const organizationNpi =
        obj.organization.identifier?.find(
          (identifier) =>
            identifier.system ===
              "http://terminology.hl7.org/NamingSystem/npi" ||
            identifier.system === "http://hl7.org/fhir/sid/us-npi",
        )?.value ?? null

      return {
        id,
        name:
          obj.organization.name ??
          obj.roleDetails?.organization.display ??
          null,
        npi: organizationNpi,
        locations: obj.locations.filter(
          (location) =>
            location.name ||
            location.address ||
            (location.contact?.length ?? 0) > 0,
        ),
        endpoints: obj.endpoints.filter(
          (endpoint) => endpoint?.connectionType || endpoint?.address,
        ),
      }
    })
  }

  get primaryOrganizationName(): string | null {
    return this.organizationCards[0]?.name ?? null
  }
}
