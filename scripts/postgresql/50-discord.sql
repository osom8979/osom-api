drop table public.discord_register;

create table
    public.discord_register
(
    channel_id int8 primary key,
    created_at timestamptz not null default now(),
    updated_at timestamptz
);

alter table public.discord_register
    enable row level security;
