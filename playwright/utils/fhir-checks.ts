import { PractitionerData } from "../tests/local/constants"
import { expect } from '@playwright/test';
import { NameData, AddressData } from "../tests/local/constants";

export const AddressTypeMapping = {
    "MAILING": 'postal',
    "LOCATION": 'physical',
}

export async function testNPI(npiResponse: any, testData: PractitionerData){
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
        expect(npiResponse.period.start.split('T')[0]).toEqual(testData.basic.enumerationDate);
        if (testData.basic.deactivationDate) {
            expect(npiResponse.period).toHaveProperty('end');
            expect(npiResponse.period.end.split('T')[0].toEqual(testData.basic.deactivationDate));
        }
}

export async function testTaxonomies(qualificationResponse: any, testData: PractitionerData){
    const taxonomies = qualificationResponse.filter(qualification => qualification.code.coding[0].system == "http://nucc.org/provider-taxonomy");
    testData.taxonomies.forEach(testDataTaxonomy => {
        const filtered_taxonomies = taxonomies.filter(taxonomy => taxonomy.code.coding[0].code == testDataTaxonomy.code);
        expect(filtered_taxonomies.length).toBeGreaterThan(0);
        expect(filtered_taxonomies[0].code.coding[0].display).toEqual(testDataTaxonomy.desc);
        // TODO: improve
    })
}

export async function testNames(nameResponse: any, testData: PractitionerData){
    const practitioner_names: Array<NameData> = [{
                "code": "1",
                "firstName": testData.basic.firstName,
                "lastName": testData.basic.lastName,
                "type": 'OFFICIAL'
            }, ...testData.otherNames]
    practitioner_names.forEach(practitioner_name => {
        const filtered_name = nameResponse.filter(name => name.text == [practitioner_name.firstName, practitioner_name.middleName, practitioner_name.lastName].join(' '));
            expect(filtered_name.length).toBeGreaterThanOrEqual(1);
            expect(filtered_name[0].family = practitioner_name?.lastName)
            // TODO: improve
        })
}

export async function testAddresses(addressResponse: any, testData: PractitionerData){
    const testAddresses: Array<AddressData> = [...testData.addresses, ...testData.practiceLocations];
    testAddresses.forEach(testAddress => {
        const filtered_address = addressResponse.filter(address => address.line.includes(testAddress.addressLine1) && address.city == testAddress.city && address.state == testAddress.state && address.postalCode == testAddress.postalCode);
        expect(filtered_address.length).toBeGreaterThanOrEqual(1);
        expect(filtered_address[0].type = AddressTypeMapping[testAddress.addressType]);
        // TODO: improve
    })
}