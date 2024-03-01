# -*- coding: utf-8 -*-

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from aiogram.utils.markdown import hlink
from overrides import override
from supabase.client import Client as SupabaseClient

from osom_api.db.telegram_register import registered_telegram_chat_id
from osom_api.logging.logging import logger


class RegistrationVerifierMiddleware(BaseMiddleware):
    def __init__(self, supabase: SupabaseClient) -> None:
        self.supabase = supabase

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if not await registered_telegram_chat_id(self.supabase, event.chat.id):
                logger.error(f"Not registered chat {event.chat.id}")
                link = hlink("osom.run", "https://www.osom.run/")
                return await event.reply(f"Not registered. Go to {link} and sign up!")

        return await handler(event, data)
