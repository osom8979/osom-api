drop type public.storage_type;

create type public.storage_type as enum (
    's3',
    'r2',
    'supabase'
    );
