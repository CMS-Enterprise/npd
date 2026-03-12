import { test } from '@playwright/test';

import { data } from '../../../test-data/organization-sample'

import { expectResultsToHaveProvider } from '../../../utils/fhir-checks';

import { getRandomNPIRecords, getSpecificNPIRecords } from '../../../utils/random-sample';
import { OrganizationDataType } from '../../../test-data/types';

let testData: Array<OrganizationDataType> = [data];

const type = 2;

test.beforeAll( async({request}) => {
    var npiList = process.env.NPI_LIST?.split(",") ?? [];
    if (npiList.length > 0) {
        testData = await getSpecificNPIRecords(request, npiList, type)
    }
    else if (Boolean(process.env.RANDOM_SAMPLE?.toLowerCase()) === true){
        testData = await getRandomNPIRecords(request, 10, type);
    }
    else {
        testData = [data]
    }
})

// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877
test.describe('As a developer, I want to search for Organizations by name and location so that I can find providers matching specific criteria', () => {
    for (const record of testData) {
        test(`NPI: ${record.number} - Can search by name`, async ({request})=>{
            // Search by name
            const nameSearch = `/fhir/Organization/?page_size=1000&name=${record.basic.name}`;
            await expectResultsToHaveProvider(nameSearch, record, request, 'Organization')
        })
        test(`NPI: ${record.number} - Can search by other name`, async ({request})=>{
            // Search by other name
            let i = 0;
            while (i+1 < record.otherNames.length) {
                const alias = record[i];
                const nameSearch = `/fhir/Organization/?page_size=1000&name=${alias}`;
                await expectResultsToHaveProvider(nameSearch, record, request, 'Organization')
                i++;
            }
        })
        test(`NPI: ${record.number} - Can search by address`, async ({request})=>{
            // Search by Location
            const addressSearch = `/fhir/Organization/?page_size=1000&address=${record.addresses[0].addressLine1}`;
            await expectResultsToHaveProvider(addressSearch, record, request, 'Organization')
        })
        test(`NPI: ${record.number} - Can search by full name and address`, async ({request})=>{

            // Search by Name and Location
            const nameAddressSearch = `/fhir/Organization/?page_size=1000&address=${record.addresses[0].addressLine1}&name=${record.basic.name}`;
            await expectResultsToHaveProvider(nameAddressSearch, record, request, 'Organization')
        })
    }
})
