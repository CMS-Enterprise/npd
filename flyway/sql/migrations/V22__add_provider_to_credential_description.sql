ALTER TABLE npd.provider_to_credential
ADD COLUMN IF NOT EXISTS credential_description text;
