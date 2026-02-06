alter table npd.npi alter column replacement_npi type bigint using replacement_npi::bigint;
alter table npd.address drop constraint fk_address_address_us_id;
alter table npd.address_us alter column id type bigint using id::bigint;
alter table npd.address alter column address_us_id type bigint using address_us_id::bigint;
alter table npd.address add constraint fk_address_address_us_id foreign key (address_us_id) references npd.address_us(id);