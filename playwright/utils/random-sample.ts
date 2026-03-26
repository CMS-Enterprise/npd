import { OrganizationDataType, PractitionerDataType } from "../test-data/types"

function calculateNpiCheckDigit(npi9: string | number): string {
  const npiString = String(npi9);
  // Base sum for NPIs is 24
  let sum = 24;
  let isEven = false;

  for (let i = npiString.length - 1; i >= 0; i--) {
    let digit = parseInt(npiString.charAt(i), 10);

    if (isEven) {
      digit *= 2;
      if (digit > 9) {
        digit -= 9;
      }
    }

    sum += digit;
    isEven = !isEven;
  }

  const checkDigit = (10 - (sum % 10)) % 10;
  return String(checkDigit);
}


export const getRandomNPI = (): string => {
    // The actual world of NPI numbers that have been assigned is smaller than the world of possibilities, so we are using the first 9 digits of the smallest and largest assigned NPIs to narrow things down.
    const min: number = 100300010;
    const max: number = 199299989;
    const randomNpi9 = Math.floor(Math.random() * (max - min) + min);

    const checkDigit = calculateNpiCheckDigit(randomNpi9);
  
    return String(randomNpi9) + checkDigit;
};


export async function getRandomNPIRecords(quantity){

    let records = {type1: [], type2: []};
    let i = 0;
    while ((records.type1.length<quantity || records.type1.length<quantity) && i<1000){
        var randomNPI = getRandomNPI();
        const response = await fetch(`https://npiregistry.cms.hhs.gov/api/?version=2.1&number=${randomNPI}`);
        const body = await response.json();
        if (body.result_count>0 ){
            if(body.results[0].enumeration_type == "NPI-1" && records.type1.length<quantity){
                records.type1.push(body.results[0]);
            }
            else if (records.type1.length<quantity){
                records.type2.push(body.results[0]);
            }
        }
        i++;
    };
    return records;
}


export async function getSpecificNPIRecords(npi_list) {
    let records = {type1: [], type2: []};
    let i = 0;
    while (i+1 < npi_list.length){
        var npi = npi_list[i]
        const response = await fetch(`https://npiregistry.cms.hhs.gov/api/?version=2.1&number=${npi}`);
        const body = await response.json();
        if (body.result_count>0 ){
            if(body.results[0].enumeration_type == "NPI-1"){
                records.type1.push(body.results[0]);
            }
            else {
                records.type2.push(body.results[0]);
            }
        }
        i++;
    };
    return records;
}