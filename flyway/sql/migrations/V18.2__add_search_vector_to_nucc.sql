alter table npd.nucc add search_vector tsvector 
GENERATED ALWAYS AS (to_tsvector('english', display_name)) STORED;
create index idx_nucc_search on npd.nucc using GIN(search_vector);
