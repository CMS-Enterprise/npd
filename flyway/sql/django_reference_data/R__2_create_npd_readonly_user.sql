DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'npd_readonly_db_user') THEN
        CREATE USER npd_readonly_db_user WITH PASSWORD '${npdReadonlyUserPassword}';
    ELSE
        ALTER USER npd_readonly_db_user WITH PASSWORD '${npdReadonlyUserPassword}';
    END IF;
END
$$;

GRANT pg_read_all_data TO npd_readonly_db_user;