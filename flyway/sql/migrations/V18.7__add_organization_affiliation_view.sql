CREATE MATERIALIZED VIEW npd.organization_affiliation AS
SELECT
    o.id AS organization_id,
    ev.id AS ehr_vendor_id,
    md5(o.id::text || '-' || ev.id::text) AS id,
    MIN(otn.name) AS organization_name,
    ev.name AS ehr_vendor_name,
    co.npi AS npi,
    array_agg(DISTINCT l.id) AS location_ids,
    array_agg(DISTINCT ei.id) AS endpoint_instance_ids,
    array_agg(DISTINCT ott.nucc_code) AS taxonomy_codes
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
    ON otn.organization_id = o.id
JOIN npd.organization_to_taxonomy ott
    ON ott.npi = co.npi
GROUP BY o.id, ev.id, ev.name, co.npi;