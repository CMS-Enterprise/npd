
alter table npd.individual_to_name add search_vector tsvector 
GENERATED ALWAYS AS (to_tsvector('english', first_name || ' ' || COALESCE(middle_name, '') || ' ' || last_name)) STORED;
create index idx_individual_to_name_search on npd.individual_to_name using GIN(search_vector);
create index on npd.provider(npi);
create index on npd.individual_to_name(individual_id);
create index on npd.individual_to_name(last_name);
create index on npd.individual_to_name(first_name);
CREATE INDEX IF NOT EXISTS idx_individualbyname_on_first_name_last_name ON npd.individual_to_name (first_name ASC, last_name ASC);