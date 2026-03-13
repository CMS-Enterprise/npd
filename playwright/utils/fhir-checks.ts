import { PractitionerDataType, NameDataType, FullAddressDataType, OrganizationDataType, OrganizationNameDataType } from "../test-data/types"
import { expect } from '@playwright/test';

export const AddressTypeMapping = {
    "MAILING": 'postal',
    "LOCATION": 'physical',
}

const base_url = process.env.BASE_URL

export async function testHasFhirResults(response:any, testData: PractitionerDataType | OrganizationDataType, resource: string){
    // Assert the status code
    expect(response.status()).toBe(200);
    
    // Get the 'content-type' header value
    const contentType = response.headers()['content-type'];
    
    // Assert that the content type contains the expected value (application/fhir+json)
    expect(contentType).toContain('application/fhir+json');
    
    // Get the response body as JSON
    const body = await response.json();
    
    //Check for basic elements of the FHIR response
    expect(body).toHaveProperty('count');
    expect(body.count).toBeGreaterThan(0);
    expect(body.results.resourceType).toEqual('Bundle');
    if (body.results.total>body.count){
        expect(body.next).not.toBeNull()
    }
    const entry = body.results.entry[0];
    expect(entry).toHaveProperty('resource');
    const fhirResource = entry.resource;
    expect(fhirResource).toHaveProperty('identifier');
    expect(fhirResource.resourceType).toEqual(resource);
    const id = fhirResource.id;
    const resourceUrl = entry.fullUrl;
    expect(resourceUrl).toEqual(`${base_url?.replace('https://','http://')}/fhir/${resource}/${id}`); // TODO: update reference URLs in FHIR API to use https instead of http
    return body  
}

export function testNPI(npiResponse: any, testData: PractitionerDataType | OrganizationDataType){
        expect(npiResponse).toHaveProperty('use');
        expect(npiResponse.use).toEqual('official');
        expect(npiResponse).toHaveProperty('value');
        expect(npiResponse.value).toEqual(testData.number);
        expect(npiResponse).toHaveProperty('type');
        expect(npiResponse.type).toEqual({
                "coding": [
                  {
                    "system": "http://terminology.hl7.org/CodeSystem/v2-0203",
                    "code": "PRN",
                    "display": "Provider number"
                  }
                ]
              });
        expect(npiResponse).toHaveProperty('period');
        expect(npiResponse.period).toHaveProperty('start');
        expect(npiResponse.period.start.split('T')[0]).toEqual(testData.basic.enumeration_date);
        if (testData.basic.deactivation_date) {
            expect(npiResponse.period).toHaveProperty('end');
            expect(npiResponse.period.end.split('T')[0].toEqual(testData.basic.deactivation_date));
        }
}

export function testTaxonomies(qualificationResponse: any, testData: PractitionerDataType | OrganizationDataType){
    const taxonomies = qualificationResponse.filter(qualification => qualification.code.coding[0].system == "http://nucc.org/provider-taxonomy");
    testData.taxonomies.forEach(testDataTaxonomy => {
        const filtered_taxonomies = taxonomies.filter(taxonomy => taxonomy.code.coding[0].code == testDataTaxonomy.code);
        expect(filtered_taxonomies.length).toBeGreaterThan(0);
        expect(filtered_taxonomies[0].code.coding[0].display).toEqual(testDataTaxonomy.desc);
        // TODO: improve
    })
}

export function testNames(fhirResource: any, testData: PractitionerDataType ){
    const names = fhirResource.name;
    expect(names.length).toEqual(testData.other_names.length + 1);
    const practitioner_names: Array<NameDataType> = [{
                "code": "1",
                "name_prefix": testData.basic.name_prefix,
                "first_name": testData.basic.first_name,
                "middle_name": testData.basic.middle_name,
                "last_name": testData.basic.last_name,
                "type": 'OFFICIAL'
            }, ...testData.other_names]
    practitioner_names.forEach(practitioner_name => {
        const filtered_name = names.filter(name => name.text.toLowerCase() == [practitioner_name.name_prefix, practitioner_name.first_name, practitioner_name.middle_name, practitioner_name.last_name].join(' ').toLowerCase());
            expect(filtered_name.length).toBeGreaterThanOrEqual(1);
            expect(filtered_name[0].family = practitioner_name?.last_name)
            // TODO: improve
        })
}

export function testOrganizationNames(fhirResource: any, testData: OrganizationDataType ){
    const allNames = [fhirResource.name, ...fhirResource.alias]
    const organization_names: Array<OrganizationNameDataType> = [{
            code: "",
            organization_name: testData.basic.organization_name,
            type: "",
        }, ...testData.other_names]
    organization_names.forEach(organization_name => {
        const filtered_name = allNames.filter(name => name.toLowerCase() == organization_name.organization_name.toLowerCase());
            expect(filtered_name.length).toBeGreaterThanOrEqual(1);
            // TODO: improve
        })
}

export function testAddresses(addressResponse: any, testData: PractitionerDataType | OrganizationDataType){
    const testAddresses: Array<FullAddressDataType> = [...testData.addresses, ...testData.practiceLocations];
    testAddresses.forEach(testAddress => {
        const filtered_address = addressResponse.filter(address => address.line.includes(testAddress.address_1) && address.city == testAddress.city && address.state == testAddress.state && address.postalCode == testAddress.postal_code);
        expect(filtered_address.length).toBeGreaterThanOrEqual(1);
        expect(filtered_address[0].type = AddressTypeMapping[testAddress.address_type]);
        // TODO: improve
    })
}

export async function testTelecoms(telecomResponse: any, testData: PractitionerDataType | OrganizationDataType){
    const testAddresses: Array<FullAddressDataType> = [...testData.addresses, ...testData.practiceLocations];
    const testNumbers = testAddresses.map(address => address.telephone_number);
    testNumbers.forEach(testNumber => {
        const filtered_telecom = telecomResponse.filter(telecom => telecom.system == "phone" && telecom.value == testNumber)
        expect(filtered_telecom.length).toBeGreaterThanOrEqual(1);
    })
    const testFaxes = testAddresses.map(address => address.fax_number);
    testFaxes.forEach(testFax => {
        const filtered_telecom = telecomResponse.filter(telecom => telecom.system == "fax" && telecom.value == testFax)
        expect(filtered_telecom.length).toBeGreaterThanOrEqual(1);
    })
}

export async function expectResultsToHaveProvider(url: string, testData: PractitionerDataType | OrganizationDataType, request: any, resource: 'Practitioner' | 'Organization') {
    var next: string | null = url;
    var found: boolean = false;
    
    while (next !== null && !found){
        const response = await request.get(next);
    
        var body = await testHasFhirResults(response, testData, resource)
    
        const entries = body.results.entry;
    
        entries.forEach(entry => {
            const npi = entry.resource.identifier.filter(identifier => identifier.system == "http://terminology.hl7.org/NamingSystem/npi")[0];
            if (npi.value == testData.number) {
                found = true;
            }
            
        })
    
        next = body.next;
    }
    expect(found).toBeTruthy();
}