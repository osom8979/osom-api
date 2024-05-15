drop table public.reply;
drop table public.msg;

create table
    public.msg
(
    id         uuid primary key,
    provider   provider_type not null,
    message_id int8                                default null,
    channel_id int8                                default null,
    username   text check (length(username) < 256) default null,
    nickname   text check (length(nickname) < 256) default null,
    content    text                                default null,
    created_at timestamptz   not null              default now()
);

create table
    public.reply
(
    msg        uuid references public.msg (id) on delete cascade on update cascade,
    content    text                 default null,
    error      text                 default null,
    created_at timestamptz not null default now()
);

alter table public.msg
    enable row level security;
alter table public.reply
    enable row level security;
