# -*- coding: utf-8 -*-

from asyncio import to_thread

from supabase import Client as SupabaseClient

# table
telegram_register = "telegram_register"

# columns
chat_id = "chat_id"
created_at = "created_at"
updated_at = "updated_at"


def _select_telegram_chat_id(supabase: SupabaseClient, message_chat_id: int):
    return (
        supabase.table(telegram_register)
        .select(chat_id)
        .eq(chat_id, message_chat_id)
        .execute()
    )


async def registered_telegram_chat_id(
    supabase: SupabaseClient,
    message_chat_id: int,
) -> bool:
    response = await to_thread(_select_telegram_chat_id, supabase, message_chat_id)
    assert len(response.data) in (0, 1)
    return len(response.data) == 1
