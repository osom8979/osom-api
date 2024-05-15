drop type public.flow_type;

create type public.flow_type as enum (
    'request',
    'response'
    );
