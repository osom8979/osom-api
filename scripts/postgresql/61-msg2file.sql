drop table public.msg2file;

create table
    public.msg2file
(
    msg  uuid references public.msg (id) on delete cascade on update cascade,
    file uuid references public.file (id) on delete cascade on update cascade,
    unique (msg, file),
    flow flow_type not null
);

create index msg2file_msg_key on public.msg2file using btree (msg);
create index msg2file_file_key on public.msg2file using btree (file);

alter table public.msg2file
    enable row level security;
