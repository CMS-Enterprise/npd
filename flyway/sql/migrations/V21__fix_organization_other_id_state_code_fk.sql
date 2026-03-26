--We had a wonky value or two in the sample data and need to fix it before moving the fk over to the organizaiton_to_other_id table
update npd.organization_to_other_id set state_code = '11' where state_code not in (select id from npd.fips_state);

--This fk was accidentally created on the provider_to_other_id table, so we remove it from that one and recreate it on the organization_to_other_id table
ALTER TABLE IF EXISTS npd.provider_to_other_id
    DROP CONSTRAINT IF EXISTS fk_organization_to_other_id_state_code;

ALTER TABLE IF EXISTS npd.organization_to_other_id
    ADD CONSTRAINT fk_organization_to_other_id_state_code FOREIGN KEY (state_code)
    REFERENCES npd.fips_state (id)