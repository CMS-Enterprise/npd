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

// NOTE: (@abachman-dsac) due to limitations in the fhir.resource.R4B model
// definitions, we cannot fully generate response types automatically
export interface FHIROrganization extends Organization {
  identifier?: FHIRIdentifer[] | null
  contact?: ExtendedContactDetail[] | null
  address?: Address[] | null
}

export interface FHIRIdentifer extends Identifier {
  type?: FHIRCodeableConcept
  period?: Period
}

export interface FHIRCodeableConcept extends CodeableConcept {
  coding?: Coding[]
  text?: string
}

export interface FHIRPractitioner extends Practitioner {
  name?: HumanName[] | null
  identifier?: FHIRIdentifer[] | null
  telecom?: ContactPoint[] | null
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
