# -*- coding: utf-8 -*-

from typing import Optional

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables
from osom_api.exceptions import InsertError


class T(Tables):
    msg = AutoName()


class C(Columns):
    id = AutoName()
    provider = AutoName()
    message_id = AutoName()
    channel_id = AutoName()
    username = AutoName()
    nickname = AutoName()
    content = AutoName()
    created_at = AutoName()


class Msg(DbMixinBase):
    async def select_msg(self, msg_uuid: str):
        return await self.supabase.table(T.msg).select("*").eq(C.id, msg_uuid).execute()

    async def insert_msg(
        self,
        msg_uuid: str,
        provider: str,
        message_id: Optional[int] = None,
        channel_id: Optional[int] = None,
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        content: Optional[str] = None,
        created_at: Optional[str] = None,
    ) -> None:
        obj = {
            C.id: msg_uuid,
            C.provider: provider,
            C.message_id: message_id,
            C.channel_id: channel_id,
            C.username: username,
            C.nickname: nickname,
            C.content: content,
        }
        if created_at:
            obj[C.created_at] = created_at

        response = await self.supabase.table(T.msg).insert(obj).execute()

        if len(response.data) == 0:
            raise InsertError(T.msg)

        assert len(response.data) == 1
        assert response.data[0][C.id] == msg_uuid
