-- DRF Spectacular documentation was reading from the model definition and not the API construction (indicating that Practitioners could be retrieved by NPI), so these migrations update the database to reflect the querying pattern in the API (Practitioners retrieved by individual_id)
alter table npd.provider_education drop constraint fk_provider_education_npi;
alter table npd.provider_to_other_id drop constraint fk_provider_to_other_id_npi;
alter table npd.provider_to_taxonomy drop constraint fk_provider_to_taxonomy_npi;
alter table npd.provider drop constraint pk_provider;
alter table npd.provider alter column individual_id set not null;
alter table npd.provider add constraint pk_provider primary key (individual_id);
alter table npd.provider add constraint uc_provider_npi UNIQUE (npi);
alter table npd.provider_education add constraint fk_provider_education_npi foreign key (npi) references npd.provider(npi);
alter table npd.provider_to_other_id add constraint fk_provider_to_other_id_npi foreign key (npi) references npd.provider(npi);
alter table npd.provider_to_taxonomy add constraint fk_provider_to_taxonomy_npi foreign key (npi) references npd.provider(npi);