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

export type AddressData = {
            "addressLine1": string,
            "addressLine2": string,
            "addressPurpose": string,
            "addressType": string,
            "city": string,
            "countryCode": string,
            "countryName": string,
            "faxNumber": string,
            "postalCode": string,
            "state": string,
            "teleNumber": string
        }
export type IdentifierData = {
            "identifier": string,
            "code": string,
            "desc": string,
            "state": string
        }
export type NameData = {
            "code": string,
            "firstName": string,
            "middleName"? : string
            "lastName": string,
            "type": string
        }
export type TaxonomyData = {
            "code": string,
            "desc": string,
            "groupCode": string,
            "license": string,
            "primary": true,
            "specialization": string,
            "state": string
        }
export type PractitionerData = {
    "addresses": Array<AddressData>,
    "basic": {
        "credential": string,
        "enumerationDate": string,
        "deactivationDate"? : string,
        "firstName": string,
        "gender": string,
        "lastName": string,
        "lastUpdated": string,
        "middleName"? : string,
        "name": string,
        "namePrefix": string,
        "soleProprietor": string,
        "status": string
    },
    "endPoints": Array<null>,
    "enumerationType": string,
    "identifiers": Array<IdentifierData>,
    "number": string,
    "otherNames": Array<NameData> | [],
    "practiceLocations": Array<AddressData> | [],
    "taxonomies": Array<TaxonomyData>
}