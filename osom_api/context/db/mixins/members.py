# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables


class T(Tables):
    members = AutoName()


class C(Columns):
    team = AutoName()
    member = AutoName()
    role = AutoName()


class Members(DbMixinBase):
    async def select_members(self):
        return (
            await self.supabase.table(T.members)
            .select(C.team, C.member, C.role)
            .execute()
        )
