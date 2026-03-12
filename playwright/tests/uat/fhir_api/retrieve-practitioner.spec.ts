import { test, expect } from '@playwright/test';

import { data } from '../../../test-data/practitioner-sample'

import { testNPI, testNames, testTaxonomies, testAddresses, testTelecoms, testHasFhirResults } from '../../../utils/fhir-checks';

import { getRandomNPIRecords, getSpecificNPIRecords } from '../../../utils/random-sample';
import { PractitionerDataType } from '../../../test-data/types';

var testData: Array<PractitionerDataType> = [data];

const type = 1;

test.beforeAll( async({request}) => {
    var npiList = process.env.NPI_LIST?.split(",")
    if (npiList !== undefined && npiList.length >0) {
        testData = await getSpecificNPIRecords(request, npiList, 1)
    }
    else if (Boolean(process.env.RANDOM_SAMPLE?.toLowerCase()) === true){
        testData = await getRandomNPIRecords(request, 10, 1);
    }
    else {
        testData = [data]
    }
})


// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877
test.describe('As a developer, I want to retrieve a Practitioner resource by NPI so that I can get provider demographic information in FHIR format', () => { 
    for (const record of testData) {
        test(`NPI: ${record.number}Is a valid FHIR response`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);
            await testHasFhirResults(response, record, 'Practitioner')
            });
        test(`NPI: ${record.number}Has expected NPI`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that NPI data are being returned properly and match the requested data
            const identifiers = resource.identifier;
            expect(identifiers.length).toBeGreaterThan(0);
            const npi = identifiers.filter(identifier => identifier.system == "http://terminology.hl7.org/NamingSystem/npi")[0];
            testNPI(npi, record)
        });
        test(`NPI: ${record.number}Has expected name(s)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that name data are being returned properly and match the expected data
            testNames(resource, record)
        });
        test(`NPI: ${record.number}Has expected taxonomy(ies)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that taxonomy data are being returned properly and match the expected data
            expect(resource).toHaveProperty('qualification')
            expect(resource.qualification.length).toEqual(record.taxonomies.length);
            testTaxonomies(resource.qualification, record);
        });
        test(`NPI: ${record.number}Has expected address(es)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that address data are being returned properly and match the expected data
            expect(resource).toHaveProperty('address');
            testAddresses(resource.address, record);
        });
        test(`NPI: ${record.number}Has expected phone(s)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that phone data are being returned properly and match the expected data
            expect(resource).toHaveProperty('telecom');
            testTelecoms(resource.telecom, record);
        });
    }
}); 
    