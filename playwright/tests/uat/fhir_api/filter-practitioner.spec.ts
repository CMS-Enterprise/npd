import { test } from '@playwright/test';

import { practitioner_data } from '../../../test-data/practitioner'

import { expectResultsToHaveProvider } from '../../../utils/fhir-checks';


// These tests are based on the FHIR API User Stories Found in This Epic: https://jiraent.cms.gov/browse/NDH-877

    test.describe('As a developer, I want to search for Practitioners by name and location so that I can find providers matching specific criteria', () => {
        test('Can search by full name', async ({request})=>{
            // Search by Full Name
            const fullNameSearch = `/fhir/Practitioner/?page_size=1000&name=${practitioner_data.basic.firstName} ${practitioner_data.basic.lastName}`;
            await expectResultsToHaveProvider(fullNameSearch, practitioner_data, request, 'Practitioner')
        })
        test('Can search by first name', async ({request})=>{
            // Search by First Name
            const firstNameSearch = `/fhir/Practitioner/?page_size=1000&name=${practitioner_data.basic.firstName}`;
            await expectResultsToHaveProvider(firstNameSearch, practitioner_data, request, 'Practitioner')
        })
        test('Can search by last name', async ({request})=>{
            // Search by Last Name
            const lastNameSearch = `/fhir/Practitioner/?page_size=1000&name=${practitioner_data.basic.lastName}`;
            await expectResultsToHaveProvider(lastNameSearch, practitioner_data, request, 'Practitioner')
        })
        test('Can search by address', async ({request})=>{
            // Search by Location
            const addressSearch = `/fhir/Practitioner/?page_size=1000&address=${practitioner_data.addresses[0].addressLine1}`;
            await expectResultsToHaveProvider(addressSearch, practitioner_data, request, 'Practitioner')
        })
        test('Can search by full name and address', async ({request})=>{

            // Search by Name and Location
            const nameAddressSearch = `/fhir/Practitioner/?page_size=1000&address=${practitioner_data.addresses[0].addressLine1}&name=${practitioner_data.basic.firstName} ${practitioner_data.basic.lastName}`;
            await expectResultsToHaveProvider(nameAddressSearch, practitioner_data, request, 'Practitioner')
        })
    })
