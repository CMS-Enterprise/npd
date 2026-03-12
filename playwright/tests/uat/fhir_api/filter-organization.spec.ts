import { test } from '@playwright/test';

import { organization_data } from '../../../test-data/organization'

import { expectResultsToHaveProvider } from '../../../utils/fhir-checks';


// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877

    test.describe('As a developer, I want to search for Organizations by name and location so that I can find providers matching specific criteria', () => {
        test('Can search by name', async ({request})=>{
            // Search by name
            const nameSearch = `/fhir/Organization/?page_size=1000&name=${organization_data.basic.name}`;
            await expectResultsToHaveProvider(nameSearch, organization_data, request, 'Organization')
        })
        test('Can search by other name', async ({request})=>{
            // Search by other name
            let i = 0;
            while (i < organization_data.otherNames.length) {
                const alias = organization_data[i];
                const nameSearch = `/fhir/Organization/?page_size=1000&name=${alias}`;
                await expectResultsToHaveProvider(nameSearch, organization_data, request, 'Organization')
                i++;
            }
        })
        test('Can search by address', async ({request})=>{
            // Search by Location
            const addressSearch = `/fhir/Organization/?page_size=1000&address=${organization_data.addresses[0].addressLine1}`;
            await expectResultsToHaveProvider(addressSearch, organization_data, request, 'Organization')
        })
        test('Can search by full name and address', async ({request})=>{

            // Search by Name and Location
            const nameAddressSearch = `/fhir/Organization/?page_size=1000&address=${organization_data.addresses[0].addressLine1}&name=${organization_data.basic.name}`;
            await expectResultsToHaveProvider(nameAddressSearch, organization_data, request, 'Organization')
        })
    })
