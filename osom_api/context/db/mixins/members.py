# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import Columns, DbMixinBase, Tables


class T(Tables):
    members = "members"


class C(Columns):
    team = "team"
    member = "member"
    role = "role"


class Members(DbMixinBase):
    async def get_members(self):
        return (
            await self.supabase.table(T.members)
            .select(C.team, C.member, C.role)
            .execute()
        )
