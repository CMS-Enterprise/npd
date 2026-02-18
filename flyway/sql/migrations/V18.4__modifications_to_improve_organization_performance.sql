create materialized view npd.organization_view as select id, authorized_official_id, ein_id, parent_id, name 
from npd.organization 
left join (select CASE
        -- Check if any row in the group has the boolean as TRUE
        WHEN BOOL_OR(is_primary) IS TRUE THEN
            -- If yes, find the minimum value among only the TRUE rows
            MIN(name) FILTER (WHERE is_primary IS TRUE)
        ELSE
            -- If not (all are FALSE or NULL), find the minimum value among all rows
            MIN(name)
    END AS name, organization_id from npd.organization_to_name group by organization_id) on organization_id = id;

create index on npd.organization_view(name);

alter table npd.organization_to_name add column search_vector tsvector 
GENERATED ALWAYS AS (to_tsvector('english', name)) STORED;
create index idx_organization_search on npd.organization_to_name using GIN(search_vector);