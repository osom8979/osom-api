# -*- coding: utf-8 -*-

from osom_api.context.db.mixins._base import AutoName, Columns, DbMixinBase, Tables


class T(Tables):
    discord_register = AutoName()


class C(Columns):
    channel_id = AutoName()
    created_at = AutoName()
    updated_at = AutoName()


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
