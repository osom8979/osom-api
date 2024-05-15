# -*- coding: utf-8 -*-

from typing import Any

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables
from osom_api.exceptions import InsertError


class T(Tables):
    openai_chat = AutoName()


class C(Columns):
    msg = AutoName()
    request = AutoName()
    response = AutoName()
    created_at = AutoName()


class OpenaiChat(DbMixinBase):
    async def insert_openai_chat(
        self, msg_uuid: str, request: Any, response: Any
    ) -> None:
        response = (
            await self.supabase.table(T.openai_chat)
            .insert({C.msg: msg_uuid, C.request: request, C.response: response})
            .execute()
        )

        if len(response.data) == 0:
            raise InsertError(T.openai_chat)

        assert len(response.data) == 1
        assert response.data[0][C.msg] == msg_uuid
