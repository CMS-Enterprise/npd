import { OrganizationDataType, PractitionerDataType } from "../test-data/types"

export const getRandomNPI = (): number => {
    const min: number = 1003000100;
    const max: number = 1992999890;
    return Math.floor(Math.random() * (max - min) + min);
};

export async function getRandomNPIRecords(request, quantity, type: 1): Promise<(Array<PractitionerDataType>)>;
export async function getRandomNPIRecords(request, quantity, type: 2): Promise<(Array<OrganizationDataType>)>;
export async function getRandomNPIRecords(request, quantity, type: 1 | 2): Promise<(Array<PractitionerDataType> | Array<OrganizationDataType>)> {
    var enumerationType: string = `NPI-${type}`;
    var records;
    while (records.length<quantity && quantity<20){
        var randomNPI = getRandomNPI()
        const response = await request.get(`https://npiregistry.cms.hhs.gov/api/?version=2.1&number=${randomNPI}`);
        const body = await response.json()
        if (body.result_count>0 && body.enumerationType == enumerationType){
            records.push(body.results[0])
        }
    };
    return records;
}

export async function getSpecificNPIRecords(request, npi_list, type: 1): Promise<(Array<PractitionerDataType>)>;
export async function getSpecificNPIRecords(request, npi_list, type: 2): Promise<(Array<OrganizationDataType>)>;
export async function getSpecificNPIRecords(request, npi_list, type: 1 | 2): Promise<(Array<PractitionerDataType> | Array<OrganizationDataType>)> {
    var enumerationType: string = `NPI-${type}`;
    var records;
    let i = 0;
    while (i+1 < npi_list.length){
        var npi = npi_list[i]
        const response = await request.get(`https://npiregistry.cms.hhs.gov/api/?version=2.1&number=${npi}`);
        const body = await response.json()
        if (body.result_count>0 && body.enumerationType == enumerationType){
            records.push(body.results[0])
        }
    };
    return records;
}