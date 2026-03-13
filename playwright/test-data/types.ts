export interface AddressDataType {
            address_1: string;
            address_2?: string;
            address_type: string;
            city: string;
            country_code: string;
            country_name: string;
            state: string,
            postal_code: string;
        }
export interface FullAddressDataType extends AddressDataType {
            address_purpose: string;
            fax_number?: string;
            telephone_number?: string;
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
            name_prefix?: string;
            first_name: string;
            middle_name? : string;
            last_name: string;
            type: string;
        }
export interface OrganizationNameDataType {
            code: string;
            organization_name: string;
            type: string;
        }
export interface TaxonomyDataType {
            code: string;
            desc: string;
            primary: boolean;
            specialization?: string;
            taxonomy_group: string;
            license: string;
            state: string;
        }

export interface EndpointDataType extends AddressDataType {
            affiliation: string;
            contentOtherDescription?: string;
            contentType?: string;
            contentTypeDescription: string;
            endpoint: string;
            endpointDescription: string;
            endpointType: string;
            endpointTypeDescription: string;
            use?: string;
            useDescription: string;
        }
export interface BaseProviderDataType {
    addresses: Array<FullAddressDataType>;
    endpoints?: Array<EndpointDataType> | [];
    enumeration_type: string;
    identifiers: Array<IdentifierDataType>;
    number: string;
    practiceLocations: Array<FullAddressDataType> | [];
    taxonomies: Array<TaxonomyDataType>;
    created_epoch: string;
    last_updated_epoch: string;
}
export interface PractitionerDataType extends BaseProviderDataType {
    basic: {
        credential?: string;
        enumeration_date: string;
        deactivation_date? : string;
        first_name: string;
        last_name: string;
        last_updated: string;
        middle_name? : string;
        sex: string;
        name_prefix?: string;
        name_suffix?: string;
        sole_proprietor: string;
        status: string;
    },
    other_names?: Array<NameDataType> | [];
}

export interface OrganizationDataType extends BaseProviderDataType{
    basic: {
        authorized_official_first_name: string;
        authorized_official_last_name: string;
        authorized_official_middle_name: string;
        authorized_official_telephone_number: string;
        authorized_official_title_or_position: string;
        certification_date: string;
        enumeration_date: string;
        deactivation_date? : string;
        last_updated: string;
        organization_name: string;
        organizational_subpart: string;
        status: string;
    };
    other_names?: Array<OrganizationNameDataType> | [];
}