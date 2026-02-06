-- clean up old naming convention that caused feature flag bugs
DELETE FROM flags_flagstate WHERE name IN ('PROVIDER_LOOKUP', 'PROVIDER_LOOKUP_DETAILS');

-- seed default feature flags
INSERT INTO
    flags_flagstate (name, condition, value, required)
values
    ('SEARCH_APP', 'in_group', 'Developers', false),
    (
        'PRACTITIONER_LOOKUP',
        'in_group',
        'Developers',
        false
    ),
    (
        'PRACTITIONER_LOOKUP_DETAILS',
        'in_group',
        'Developers',
        false
    ),
    (
        'ORGANIZATION_LOOKUP',
        'in_group',
        'Developers',
        false
    ),
    (
        'ORGANIZATION_LOOKUP_DETAILS',
        'in_group',
        'Developers',
        false
    ) ON CONFLICT
DO NOTHING;