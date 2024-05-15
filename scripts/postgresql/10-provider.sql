drop type public.provider_type;

create type public.provider_type as enum (
    'anonymous',
    'user',
    'admin',
    'tester',
    'master',
    'worker',
    'discord',
    'telegram'
    );
