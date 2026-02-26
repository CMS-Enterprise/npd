export const FHIR_RESOURCES = [
    "Endpoint",
    "Location", 
    "Organization",
    "Practitioner",
    "PractitionerRole",
    "metadata",
] as const
  
export type FHIRResource = (typeof FHIR_RESOURCES)[number]

export let ORGANIZATION: { npi: string; id: string; name: string } = {
    npi: "UNSET",
    id: "UNSET",
    name: "UNSET",
}

export let PRACTITIONER: { npi: string; id: string; name: string } = {
    npi: "UNSET",
    id: "UNSET",
    name: "UNSET",
}
