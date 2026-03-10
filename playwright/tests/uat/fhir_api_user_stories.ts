import { test, expect } from '@playwright/test';

import { practitioner_data } from '../../test-data/practitioner'

import { testNPI, testNames, testTaxonomies, testAddresses } from '../../utils/fhir-checks';

const base_url = process.env.BASE_URL

test.describe('FHIR API User Stories', () => { 
    test('As a developer, I want to retrieve a Practitioner resource by NPI so that I can get provider demographic information in FHIR format', async ({request}) => {
        const response = await request.get(`/fhir/Practitioner/?identifier=NPI|${practitioner_data.number}`);

        // Assert the status code
        expect(response.status()).toBe(200);

        // Get the response body as JSON
        const body = await response.json();

        expect(body).toHaveProperty('count');
        expect(body.count).toEqual(1);
        const entry = body.results.entry[0];
        expect(entry).toHaveProperty('resource');
        const resource = entry.resource;
        expect(resource).toHaveProperty('identifier');
        const id = resource.id;
        const url = entry.fullUrl;
        expect(url).toEqual(`${base_url}/fhir/Practitioner/${id}`);
        // Validate that NPI data are being returned properly and match the requested data
        const identifiers = resource.identifier;
        expect(identifiers.length).toBeGreaterThan(0);
        const npi = identifiers.filter(identifier => identifier.system == "http://terminology.hl7.org/NamingSystem/npi")[0];
        testNPI(npi, practitioner_data)
        // Validate that name data are being returned properly and match the expected data
        expect(resource).toHaveProperty('name');
        expect(resource.name.length).toEqual(practitioner_data.otherNames.length + 1);
        testNames(resource.name, practitioner_data)
        // Validate that taxonomy data are being returned properly and match the expected data
        expect(resource).toHaveProperty('qualification')
        expect(resource.qualification.length).toEqual(practitioner_data.taxonomies.length);
        testTaxonomies(resource.qualification, practitioner_data);
        // Validate that address data are being returned properly and match the expected data
        expect(resource).toHaveProperty('address')
        testAddresses(resource.address, practitioner_data)
    });
});