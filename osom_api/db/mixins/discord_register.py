# -*- coding: utf-8 -*-

from osom_api.db.mixins._base import Columns, DbMixinBase, Tables


class T(Tables):
    discord_register = "discord_register"


class C(Columns):
    channel_id = "channel_id"
    created_at = "created_at"
    updated_at = "updated_at"


class DiscordRegister(DbMixinBase):
    async def select_discord_channel_id(self, context_channel_id: int):
        return (
            await self.supabase.table(T.discord_register)
            .select(C.channel_id)
            .eq(C.channel_id, context_channel_id)
            .execute()
        )

    async def registered_discord_channel_id(self, context_channel_id: int):
        response = await self.select_discord_channel_id(context_channel_id)
        assert len(response.data) in (0, 1)
        return len(response.data) == 1
