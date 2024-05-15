drop table public.openai_chat;

create table
    public.openai_chat
(
    msg        uuid references public.msg (id) on delete set null on update cascade,
    request    jsonb,
    response   jsonb,
    created_at timestamptz not null default now()
);

alter table public.openai_chat
    enable row level security;
