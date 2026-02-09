alter table npd.address_us add search_vector tsvector 
GENERATED ALWAYS AS (to_tsvector('english', delivery_line_1 || ' ' || COALESCE(delivery_line_2, '') || ' ' || city_name || ' ' || zipcode)) STORED;
create index idx_address_us_search on npd.address_us using GIN(search_vector);