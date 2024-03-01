drop table public.telegram_register;

create table
    public.telegram_register
(
    chat_id    int8 primary key,
    created_at timestamptz not null default now(),
    updated_at timestamptz
);

alter table public.telegram_register
    enable row level security;
