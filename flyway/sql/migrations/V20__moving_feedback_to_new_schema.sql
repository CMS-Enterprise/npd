CREATE SCHEMA IF NOT EXISTS app;
ALTER TABLE npd.feedback SET SCHEMA app;
ALTER TABLE app.feedback ADD COLUMN record_id uuid;