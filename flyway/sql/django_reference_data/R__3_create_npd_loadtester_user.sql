DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'npd_load_tester') THEN
        CREATE USER npd_load_tester WITH PASSWORD '${loadTesterPassword}';
    ELSE
        ALTER USER npd_load_tester WITH PASSWORD '${loadTesterPassword}';
    END IF;
END
$$;

GRANT pg_read_all_data TO npd_load_tester;