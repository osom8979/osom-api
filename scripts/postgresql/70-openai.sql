drop table public.openai_chat;

create table
    public.openai_chat
(
    msg_uuid   uuid primary key     default NULL,
    request    jsonb,
    response   jsonb,
    created_at timestamptz not null default now()
);

alter table public.openai_chat
    enable row level security;
