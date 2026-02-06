CREATE TYPE endpoint_status AS ENUM ('active', 'limited', 'suspended', 'error', 'off', 'entered-in-error');
alter table npd.endpoint_instance add status endpoint_status DEFAULT 'active';