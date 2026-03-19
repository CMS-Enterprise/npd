import { getRandomNPIRecords, getSpecificNPIRecords } from './utils/random-sample';
import { OrganizationDataType, PractitionerDataType } from './test-data/types';

import { data as sampleOrganization } from './test-data/organization-sample';
import { data as samplePractitioner } from './test-data/practitioner-sample';

import dotenv from 'dotenv';
import path from 'path';
dotenv.config({ path: path.resolve(__dirname, '.env') });

const randomQuantity = process.env.RANDOM_QUANTITY ?? 5

const fs = require("node:fs/promises");

let orgTestData: Array<OrganizationDataType>;
let practitionerTestData: Array<PractitionerDataType>;

(async () => {
    var npiList = process.env.NPI_LIST?.split(",") ?? [];
    if (npiList.length > 0) {
        const specificData = await getSpecificNPIRecords(npiList);
        orgTestData = specificData.type2;
        practitionerTestData = specificData.type1;
    }
    else if (Boolean(process.env.RANDOM_SAMPLE?.toLowerCase()) === true){
        const randomData = await getRandomNPIRecords(randomQuantity);
        orgTestData = randomData.type2;
        practitionerTestData = randomData.type1;
    }
    else {
        orgTestData = [sampleOrganization]
        practitionerTestData = [samplePractitioner]
    }
    fs.writeFile("test-data/tmp/organization-data.json", JSON.stringify(orgTestData));
    fs.writeFile("test-data/tmp/practitioner-data.json", JSON.stringify(practitionerTestData));
})()
