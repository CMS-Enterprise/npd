CREATE SCHEMA IF NOT EXISTS app;

CREATE TABLE app.feedback (
    id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
    record_id uuid,
    npi varchar(10),
    record_name text,
    issues text[],
    details text,
    email text,
    created_at timestamptz DEFAULT now() NOT NULL
);