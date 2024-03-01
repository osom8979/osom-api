drop table public.teams;
drop table public.members;

create table
    public.teams
(
    id         uuid primary key     default gen_random_uuid(),
    name       text        not null check (length(name) < 256),
    owner      uuid references auth.users (id) on delete set null on update cascade,
    created_at timestamptz not null default now(),
    updated_at timestamptz
);

create table
    public.members
(
    team   uuid references public.teams (id) on delete cascade on update cascade,
    member uuid references auth.users (id) on delete cascade on update cascade,
    unique (team, member),
    role   role_type not null default 'guest'::role_type
);

create index members_team_key on public.members using btree (team);
create index members_member_key on public.members using btree (member);

create function public.on_teams_update_trigger()
    returns trigger as
$$
begin
    if OLD.created_at <> NEW.created_at then
        raise exception 'Column created_at cannot be updated';
    end if;

    NEW.updated_at = now();
    return NEW;
end;
$$ language plpgsql;

create trigger teams_update_trigger
    before update
    on public.teams
    for each row
execute function public.on_teams_update_trigger();

create function public.on_members_update_trigger()
    returns trigger as
$$
begin
    if OLD.team <> NEW.team then
        raise exception 'Column team cannot be updated';
    end if;

    if OLD.member <> NEW.member then
        raise exception 'Column member cannot be updated';
    end if;

    return NEW;
end;
$$ language plpgsql;

create trigger members_update_trigger
    before update
    on public.members
    for each row
execute function public.on_members_update_trigger();

create function public.has_teams_member_permission(
    id uuid,
    owner uuid
)
    returns boolean as
$$
declare
    auth_id uuid := auth.uid();
begin
    return (
        (auth_id = owner)
            or
        (auth_id in (select member
                     from public.members as m
                     where m.team = id))
        );
end;
$$ language plpgsql;

alter table public.teams
    enable row level security;
create policy teams_insert
    on public.teams
    for insert
    to authenticated
    with check (
    auth.uid() = owner
    );
create policy teams_update
    on public.teams
    for update
    to authenticated
    using (
    auth.uid() = owner
    );
create policy teams_delete
    on public.teams
    for delete
    to authenticated
    using (
    auth.uid() = owner
    );
create policy teams_select
    on public.teams
    for select
    to authenticated
    using (
    public.has_teams_member_permission(id, owner)
    );

create function public.has_members_manager_permission(
    team uuid,
    member uuid,
    role role_type
)
    returns boolean as
$$
declare
    auth_id uuid := auth.uid();
begin
    return (
        (auth_id in (select owner from public.teams as t where t.id = team))
            or
        (auth_id = member and role = 'manager'::role_type)
        );
end;
$$ language plpgsql;

alter table public.members
    enable row level security;
create policy members_insert
    on public.members
    for insert
    to authenticated
    with check (
    public.has_members_manager_permission(team, member, role)
    );
create policy members_update
    on public.members
    for update
    to authenticated
    using (
    public.has_members_manager_permission(team, member, role)
    );
create policy members_delete
    on public.members
    for delete
    to authenticated using (
    public.has_members_manager_permission(team, member, role)
    );
create policy members_select
    on public.members
    for select
    to authenticated
    using (
    auth.uid() = member
    );
