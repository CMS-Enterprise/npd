create materialized view npd.provider_to_location_view as select 
pl.location_id, 
pl.other_address_id, 
pl.nucc_code, 
pl.specialty_id,
pl.id,
pl.provider_role_code,
pl.other_phone_id,
pl.other_endpoint_id,
pl.active,
pl.provider_to_organization_id,
l.name as location_name,
p.first_name as practitioner_first_name,
p.last_name as practitioner_last_name,
o.name as organization_name
from npd.provider_to_location pl
left join npd.provider_to_organization po on po.id = pl.provider_to_organization_id
left join npd.provider_view p on p.individual_id = po.individual_id
left join npd.organization_view o on o.id = po.organization_id
left join npd.location l on l.id = pl.location_id;


create index on npd.provider_to_location_view(practitioner_last_name, practitioner_first_name);
create index on npd.provider_to_location_view(organization_name);
create index on npd.provider_to_location_view(location_name);