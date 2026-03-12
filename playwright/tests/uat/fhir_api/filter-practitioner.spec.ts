import { test } from '@playwright/test';

import { data } from '../../../test-data/practitioner-sample'

import { expectResultsToHaveProvider } from '../../../utils/fhir-checks';

import { getRandomNPIRecords, getSpecificNPIRecords } from '../../../utils/random-sample';
import { PractitionerDataType } from '../../../test-data/types';

var testData: Array<PractitionerDataType> = [data];

const type = 1;

test.beforeAll( async({request}) => {
    var npiList = process.env.NPI_LIST?.split(",")
    if (npiList !== undefined && npiList.length >0) {
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
test.describe('As a developer, I want to search for Practitioners by name and location so that I can find providers matching specific criteria', () => {
    for (const record of testData) {
        test(`NPI: ${record.number} - Can search by full name`, async ({request})=>{
            // Search by Full Name
            const fullNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.firstName} ${record.basic.lastName}`;
            await expectResultsToHaveProvider(fullNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by first name`, async ({request})=>{
            // Search by First Name
            const firstNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.firstName}`;
            await expectResultsToHaveProvider(firstNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by last name`, async ({request})=>{
            // Search by Last Name
            const lastNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.lastName}`;
            await expectResultsToHaveProvider(lastNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by address`, async ({request})=>{
            // Search by Location
            const addressSearch = `/fhir/Practitioner/?page_size=1000&address=${record.addresses[0].addressLine1}`;
            await expectResultsToHaveProvider(addressSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by full name and address`, async ({request})=>{

            // Search by Name and Location
            const nameAddressSearch = `/fhir/Practitioner/?page_size=1000&address=${record.addresses[0].addressLine1}&name=${record.basic.firstName} ${record.basic.lastName}`;
            await expectResultsToHaveProvider(nameAddressSearch, record, request, 'Practitioner')
        })
    }
})
