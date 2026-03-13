import { test } from '@playwright/test';

import { expectResultsToHaveProvider } from '../../../utils/fhir-checks';

import data from "../../../test-data/tmp/practitioner-data.json";
import { PractitionerDataType } from '../../../test-data/types';

const testData: Array<PractitionerDataType> = data;

// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877
test.describe('As a developer, I want to search for Practitioners by name and location so that I can find providers matching specific criteria', () => {
    for (const record of testData) {
        test(`NPI: ${record.number} - Can search by full name`, async ({request})=>{
            // Search by Full Name
            const fullNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.first_name} ${record.basic.last_name}`;
            await expectResultsToHaveProvider(fullNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by first name`, async ({request})=>{
            // Search by First Name
            const firstNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.first_name}`;
            await expectResultsToHaveProvider(firstNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by last name`, async ({request})=>{
            // Search by Last Name
            const lastNameSearch = `/fhir/Practitioner/?page_size=1000&name=${record.basic.last_name}`;
            await expectResultsToHaveProvider(lastNameSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by address`, async ({request})=>{
            // Search by Location
            const addressSearch = `/fhir/Practitioner/?page_size=1000&address=${record.addresses[0].address_1}`;
            await expectResultsToHaveProvider(addressSearch, record, request, 'Practitioner')
        })
        test(`NPI: ${record.number} - Can search by full name and address`, async ({request})=>{

            // Search by Name and Location
            const nameAddressSearch = `/fhir/Practitioner/?page_size=1000&address=${record.addresses[0].address_1}&name=${record.basic.first_name} ${record.basic.last_name}`;
            await expectResultsToHaveProvider(nameAddressSearch, record, request, 'Practitioner')
        })
    }
})
