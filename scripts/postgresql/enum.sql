-- drop type public.role_type;

create type public.role_type as enum (
    'manager',
    'developer',
    'verifier',
    'editor',
    'reader',
    'guest'
    );
