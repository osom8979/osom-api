drop table public.openai_chat;

create table
    public.openai_chat
(
    id         bigserial primary key,
    request    jsonb,
    response   jsonb,
    created_at timestamptz not null default now()
);

alter table public.openai_chat
    enable row level security;
