drop table public.file;

create table
    public.file
(
    id           uuid primary key,
    provider     provider_type not null,
    storage      storage_type  not null,
    name         text check (length(name) < 256)         default null,
    content_type text check (length(content_type) < 256) default null,
    native_id    text check (length(native_id) < 512)    default null,
    created_at   timestamptz   not null                  default now(),
    updated_at   timestamptz
);

alter table public.file
    enable row level security;
