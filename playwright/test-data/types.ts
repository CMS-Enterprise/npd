export interface AddressDataType {
            addressLine1: string;
            addressLine2?: string;
            addressType: string;
            city: string;
            countryCode: string;
            countryName: string;
            state: string,
            postalCode: string;
        }
export interface FullAddressDataType extends AddressDataType {
            addressPurpose: string;
            faxNumber?: string;
            teleNumber: string;
        }
export interface IdentifierDataType {
            identifier: string;
            code: string;
            desc: string;
            state: string;
            issuer?: string;
        }
export interface NameDataType {
            code: string;
            namePrefix?: string;
            firstName: string;
            middleName? : string;
            lastName: string;
            type: string;
        }
export interface OrganizationNameDataType {
            code: string;
            organizationName: string;
            type: string;
        }
export interface TaxonomyDataType {
            code: string;
            desc: string;
            primary: boolean;
            specialization: string;
        }
export interface PractitionerTaxonomyDataType extends TaxonomyDataType {
            groupCode: string;
            license: string;
            state: string;
        }
export interface EndpointDataType extends AddressDataType {
            affiliation: string;
            contentOtherDescription: string;
            contentType: string;
            contentTypeDescription: string;
            endpoint: string;
            endpointDescription: string;
            endpointType: string;
            endpointTypeDescription: string;
            use: string;
            useDescription: string;
        }
export interface BaseProviderDataType {
    addresses: Array<FullAddressDataType>;
    endPoints: Array<EndpointDataType> | [];
    enumerationType: string;
    identifiers: Array<IdentifierDataType>;
    number: string;
    practiceLocations: Array<FullAddressDataType> | [];
}
export interface PractitionerDataType extends BaseProviderDataType {
    basic: {
        credential: string;
        enumerationDate: string;
        deactivationDate? : string;
        firstName: string;
        gender: string;
        lastName: string;
        lastUpdated: string;
        middleName? : string;
        name: string;
        namePrefix: string;
        soleProprietor: string;
        status: string;
    },
    otherNames: Array<NameDataType> | [];
    taxonomies: Array<PractitionerTaxonomyDataType>;
}

export interface OrganizationDataType extends BaseProviderDataType{
    basic: {
        aoFirstName: string;
        aoLastName: string;
        aoMiddleName: string;
        aoTeleNumber: string;
        aoTitle: string;
        certificationDate: string;
        enumerationDate: string;
        deactivationDate? : string;
        lastUpdated: string;
        name: string;
        orgName: string;
        orgSubpart: string;
        status: string;
    };
    otherNames: Array<OrganizationNameDataType> | [];
    taxonomies: Array<TaxonomyDataType>;
}