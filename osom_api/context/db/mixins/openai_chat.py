# -*- coding: utf-8 -*-

from typing import Any

from fastapi import HTTPException, status
from fastapi.types import BaseModel

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables


class T(Tables):
    openai_chat = AutoName()


class C(Columns):
    msg_uuid = AutoName()
    request = AutoName()
    response = AutoName()
    created_at = AutoName()


class InsertOpenaiChatResponse(BaseModel):
    msg_uuid: str


class OpenaiChat(DbMixinBase):
    async def insert_openai_chat(
        self, msg_uuid: str, request: Any, response: Any
    ) -> InsertOpenaiChatResponse:
        response = (
            await self.supabase.table(T.openai_chat)
            .insert({C.msg_uuid: msg_uuid, C.request: request, C.response: response})
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Not found inserted {T.openai_chat}",
            )

        assert len(response.data) == 1
        row = response.data[0]
        return InsertOpenaiChatResponse(msg_uuid=row[C.msg_uuid])
