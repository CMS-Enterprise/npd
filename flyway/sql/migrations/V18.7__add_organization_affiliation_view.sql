CREATE MATERIALIZED VIEW npd.organization_affiliation AS
SELECT DISTINCT
    o.id AS organization_id,
    ev.id AS ehr_vendor_id,
    md5(o.id::text || '-' || ev.id::text) AS id,
    otn.name AS organization_name,
    ev.name AS ehr_vendor_name,
    co.npi AS npi
FROM npd.organization o
JOIN npd.location l
    ON l.organization_id = o.id
JOIN npd.location_to_endpoint_instance ltei
    ON ltei.location_id = l.id
JOIN npd.endpoint_instance ei
    ON ei.id = ltei.endpoint_instance_id
JOIN npd.ehr_vendor ev
    ON ev.id = ei.ehr_vendor_id
JOIN npd.clinical_organization co
    ON co.organization_id = o.id
JOIN npd.organization_to_name otn
    ON otn.organization_id = o.id;