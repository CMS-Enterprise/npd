create materialized view npd.provider_view as select p.individual_id, npi, split_part(name,'+',2) as first_name, split_part(name,'+',1) last_name 
from npd.provider p
left join (select CASE
        -- Check if any row in the group has the boolean as TRUE
        WHEN min(name_use_id) = 1 THEN
            -- If yes, find the minimum value among only the TRUE rows
            MIN(last_name||'+'||first_name) FILTER (WHERE name_use_id = 1)
        ELSE
            -- If not (all are FALSE or NULL), find the minimum value among all rows
            MIN(last_name||'+'||first_name)
    END AS name, individual_id from npd.individual_to_name group by individual_id) n on p.individual_id = n.individual_id;


create index on npd.provider_view(last_name, first_name);