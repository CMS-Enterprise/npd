INSERT INTO
    auth_user (
        password,
        is_superuser,
        username,
        email,
        first_name,
        last_name,
        is_staff,
        is_active,
        date_joined
    )
SELECT
    '${loadTesterPassword}',
    true,
    'npd+load+tester@cms.hhs.gov',
    'npd+load+tester@cms.hhs.gov',
    'NPD Load',
    'Tester',
    false,
    true,
    now()
WHERE
    '${loadTesterPassword}' LIKE 'pbkdf2_sha256$%' ON CONFLICT (username)
DO
UPDATE
SET
    password = '${loadTesterPassword}';
