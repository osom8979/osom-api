drop table public.telegram_register;
drop table public.telegram_chat;
drop table public.telegram_chat_choices;

create table
    public.telegram_register
(
    chat_id    int8 primary key,
    created_at timestamptz not null default now(),
    updated_at timestamptz
);

create table
    public.telegram_chat
(
    id                      text unique primary key,
    chat_id                 int8 references public.telegram_register (chat_id) on delete set null on update cascade,
    model                   text,
    object                  text,
    system_fingerprint      text,
    usage_completion_tokens int4,
    usage_prompt_tokens     int4,
    usage_total_tokens      int4,
    request_user_id         int8        not null,
    request_user_chat       text        not null,
    created_at              timestamptz not null default now(),
    updated_at              timestamptz
);

create table
    public.telegram_chat_choices
(
    id                    bigserial primary key,
    chat_id               int8 references public.telegram_chat (chat_id) on delete set null on update cascade,
    finish_reason         text,
    index                 text,
    logprobs              text,
    message_content       text,
    message_role          text,
    message_function_call text,
    message_tool_calls    text
);

alter table public.telegram_register
    enable row level security;
alter table public.telegram_chat
    enable row level security;
alter table public.telegram_chat_choices
    enable row level security;
