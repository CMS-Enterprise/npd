import { test, expect } from '@playwright/test';

import { testNPI, testOrganizationNames, testAddresses, testTelecoms, testHasFhirResults, testTaxonomyExtension } from '../../../utils/fhir-checks';

import data from "../../../test-data/tmp/organization-data.json";
import { OrganizationDataType } from '../../../test-data/types';

const testData: Array<OrganizationDataType> = data;


// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877
test.describe('I want to retrieve Organization resources by Type 2 NPI so that I can get organizational provider information in a FHIR format', () => { 
    for (const record of testData) {
        test(`NPI: ${record.number} - Is a valid FHIR response`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);
            await testHasFhirResults(response, record, 'Organization')
            });
        test(`NPI: ${record.number} - Has expected NPI`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that NPI data are being returned properly and match the requested data
            const identifiers = resource.identifier;
            expect(identifiers.length).toBeGreaterThan(0);
            const npi = identifiers.filter(identifier => identifier.system == "http://terminology.hl7.org/NamingSystem/npi")[0];
            testNPI(npi, record)
        });
        test(`NPI: ${record.number} - Has expected name(s)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that name data are being returned properly and match the expected data
            testOrganizationNames(resource, record)
        });
        test(`NPI: ${record.number} - Has expected taxonomy(ies)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that taxonomy data are being returned properly and match the expected data
            expect(resource).toHaveProperty('qualification')
            expect(resource.qualification.length).toEqual(record.taxonomies.length);
            testTaxonomyExtension(resource.qualification, record);
        });
        test(`NPI: ${record.number} - Has expected address(es)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that address data are being returned properly and match the expected data
            expect(resource).toHaveProperty('address');
            testAddresses(resource.address, record);
        });
        test(`NPI: ${record.number} - Has expected phone(s)`, async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Organization/?identifier=NPI|${record.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that phone data are being returned properly and match the expected data
            expect(resource).toHaveProperty('telecom');
            testTelecoms(resource.telecom, record);
        });
    }
});
    
    