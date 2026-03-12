import { test, expect } from '@playwright/test';

import { practitioner_data } from '../../../test-data/practitioner'

import { testNPI, testNames, testTaxonomies, testAddresses, testTelecoms, testHasFhirResults } from '../../../utils/fhir-checks';

// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877
test.describe('As a developer, I want to retrieve a Practitioner resource by NPI so that I can get provider demographic information in FHIR format', () => { 

        test('Is a valid FHIR response', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);
            await testHasFhirResults(response, practitioner_data, 'Practitioner')
            });
        test('Has expected NPI', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that NPI data are being returned properly and match the requested data
            const identifiers = resource.identifier;
            expect(identifiers.length).toBeGreaterThan(0);
            const npi = identifiers.filter(identifier => identifier.system == "http://terminology.hl7.org/NamingSystem/npi")[0];
            testNPI(npi, practitioner_data)
        });
        test('Has expected name(s)', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that name data are being returned properly and match the expected data
            testNames(resource, practitioner_data)
        });
        test('Has expected taxonomy(ies)', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that taxonomy data are being returned properly and match the expected data
            expect(resource).toHaveProperty('qualification')
            expect(resource.qualification.length).toEqual(practitioner_data.taxonomies.length);
            testTaxonomies(resource.qualification, practitioner_data);
        });
        test('Has expected address(es)', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that address data are being returned properly and match the expected data
            expect(resource).toHaveProperty('address');
            testAddresses(resource.address, practitioner_data);
        });
        test('Has expected phone(s)', async ({request}) => {
            // Search by NPI
            const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

            const body = await response.json()

            const resource = body.results.entry[0].resource

            // Validate that phone data are being returned properly and match the expected data
            expect(resource).toHaveProperty('telecom');
            testTelecoms(resource.telecom, practitioner_data);
        });
    });
    
    