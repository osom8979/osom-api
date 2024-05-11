# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables


class T(Tables):
    telegram_register = AutoName()


class C(Columns):
    chat_id = AutoName()
    created_at = AutoName()
    updated_at = AutoName()


class TelegramRegister(DbMixinBase):
    async def select_telegram_chat_id(self, message_chat_id: int):
        return (
            await self.supabase.table(T.telegram_register)
            .select(C.chat_id)
            .eq(C.chat_id, message_chat_id)
            .execute()
        )

    async def registered_telegram_chat_id(self, message_chat_id: int):
        response = await self.select_telegram_chat_id(message_chat_id)
        assert len(response.data) in (0, 1)
        return len(response.data) == 1
