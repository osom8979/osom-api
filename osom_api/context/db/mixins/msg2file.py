# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables
from osom_api.exceptions import InsertError


class T(Tables):
    msg2file = AutoName()


class C(Columns):
    msg = AutoName()
    file = AutoName()
    flow = AutoName()


class Msg2file(DbMixinBase):
    async def select_msg2file(self, msg_uuid: str):
        return (
            await self.supabase.table(T.msg2file)
            .select("*")
            .eq(C.msg, msg_uuid)
            .execute()
        )

    async def insert_msg2file(
        self,
        msg_uuid: str,
        file_uuid: str,
        flow: str,
    ) -> None:
        obj = {C.msg: msg_uuid, C.file: file_uuid, C.flow: flow}
        response = await self.supabase.table(T.msg2file).insert(obj).execute()

        if len(response.data) == 0:
            raise InsertError(T.msg2file)

        assert len(response.data) == 1
        assert response.data[0][C.msg] == msg_uuid
        assert response.data[0][C.file] == file_uuid
