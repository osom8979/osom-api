# -*- coding: utf-8 -*-

from typing import Optional

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables
from osom_api.exceptions import InsertError


class T(Tables):
    reply = AutoName()


class C(Columns):
    msg = AutoName()
    content = AutoName()
    error = AutoName()
    created_at = AutoName()


class Reply(DbMixinBase):
    async def select_reply(self, msg_uuid: str):
        return (
            await self.supabase.table(T.reply).select("*").eq(C.msg, msg_uuid).execute()
        )

    async def insert_reply(
        self,
        msg: str,
        content: Optional[str] = None,
        error: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        obj = {C.msg: msg, C.content: content, C.error: error}
        if created_at:
            obj[C.created_at] = created_at

        response = await self.supabase.table(T.reply).insert(obj).execute()

        if len(response.data) == 0:
            raise InsertError(T.reply)

        assert len(response.data) == 1
        assert response.data[0][C.msg] == msg
