# -*- coding: utf-8 -*-

from asyncio import to_thread

from supabase import Client as SupabaseClient

# table
discord_register = "discord_register"

# columns
channel_id = "channel_id"
created_at = "created_at"
updated_at = "updated_at"


def _select_discord_channel_id(supabase: SupabaseClient, context_channel_id: int):
    return (
        supabase.table(discord_register)
        .select(channel_id)
        .eq(channel_id, context_channel_id)
        .execute()
    )


async def registered_discord_channel_id(
    supabase: SupabaseClient,
    context_channel_id: int,
) -> bool:
    response = await to_thread(_select_discord_channel_id, supabase, context_channel_id)
    assert len(response.data) in (0, 1)
    return len(response.data) == 1
