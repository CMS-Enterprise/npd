import type { Address } from "./Address"
import type { CodeableConcept } from "./CodeableConcept"
import type { Coding } from "./Coding"
import type { ContactPoint } from "./ContactPoint"
import type { ExtendedContactDetail } from "./ExtendedContactDetail"
import type { HumanName } from "./HumanName"
import type { Identifier } from "./Identifier"
import type { Organization } from "./Organization"
import type { Period } from "./Period"
import type { Practitioner } from "./Practitioner"
import type { Extension } from "./Extension"
import type { PractitionerRole } from "./PractitionerRole"
import type { Endpoint, ProtocolProfileStandardToBeUsedWithThisEndpointConnection } from "./Endpoint"
import type { Location } from "./Location"
import type { Reference } from "./Reference"

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically
export interface FHIROrganization extends Organization {
  identifier?: FHIRIdentifer[] | null
  contact?: ExtendedContactDetail[] | null
  address?: Address[] | null
  extension?: FHIRExtension[] | null
}

export interface FHIRExtension extends Extension {
  valueCodeableConcept?: FHIRCodeableConcept
}

export interface FHIRIdentifer extends Identifier {
  type?: FHIRCodeableConcept
  period?: Period
  assigner?: Reference
}

export interface FHIRCodeableConcept extends CodeableConcept {
  coding?: Coding[]
  text?: string
}

export interface FHIRReference extends Reference {
  reference: string
}

export interface FHIRPractitioner extends Practitioner {
  name?: HumanName[] | null
  identifier?: FHIRIdentifer[] | null
  telecom?: ContactPoint[] | null
  qualification?: FHIRPractitionerQualification[] | null
}

export interface FHIRPractitionerRole extends PractitionerRole {
  organization: FHIRReference
  practitioner: FHIRReference
  endpoint?: Array<FHIRReference>
  location: Array<FHIRReference>
}

export interface FHIRProtocol extends ProtocolProfileStandardToBeUsedWithThisEndpointConnection {
  [key: string]: string | any
}

export interface FHIREndpoint extends Endpoint {
  id: string
  connectionType: FHIRProtocol
}

export interface FHIRLocation extends Location {
  id: string
  address: Address
}

// generated base type is too loosely typed so made this manually
export interface FHIRPractitionerQualification {
  code: FHIRCodeableConcept
  identifier?: FHIRIdentifer[] | null
  period?: Period | null
}

export interface FHIRCollection<T> {
  count: number
  next: string | null
  previous: string | null
  results: {
    resourceType: "Bundle" | string
    type: "searchset" | string
    total: number
    entry: Array<{
      fullUrl: string
      resource: T
    }>
  }
}
