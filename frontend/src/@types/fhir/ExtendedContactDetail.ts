import type { Period } from "./Period"
import type { Address } from "./Address"
import type { ContactPoint } from "./ContactPoint"
import type { HumanName } from "./HumanName"
import type { FHIRCodeableConcept } from "."

export interface ExtendedContactDetail {
    purpose?: FHIRCodeableConcept
    name?: HumanName
    telecom?: ContactPoint[]
    address?: Address
    period?: Period
}
