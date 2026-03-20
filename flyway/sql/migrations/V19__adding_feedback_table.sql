CREATE TABLE npd.feedback (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    npi varchar(10),
    record_name text,
    issues text[],
    details text,
    email text,
    created_at timestamptz DEFAULT now() not NULL
);