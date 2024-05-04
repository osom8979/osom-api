# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import Columns, DbMixinBase, Tables


class T(Tables):
    telegram_register = "telegram_register"


class C(Columns):
    chat_id = "chat_id"
    created_at = "created_at"
    updated_at = "updated_at"


class TelegramRegister(DbMixinBase):
    async def select_discord_channel_id(self, message_chat_id: int):
        return (
            await self.supabase.table(T.telegram_register)
            .select(C.chat_id)
            .eq(C.chat_id, message_chat_id)
            .execute()
        )

    async def registered_telegram_chat_id(self, message_chat_id: int):
        response = await self.select_discord_channel_id(message_chat_id)
        assert len(response.data) in (0, 1)
        return len(response.data) == 1
