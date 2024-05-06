# -*- coding: utf-8 -*-

from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject
from overrides import override

from osom_api.arguments import NOT_REGISTERED_MSG
from osom_api.context.db import DbClient
from osom_api.logging.logging import logger


class RegistrationVerifierMiddleware(BaseMiddleware):
    def __init__(self, db: DbClient) -> None:
        self.db = db

    @override
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            if not await self.db.registered_telegram_chat_id(event.chat.id):
                logger.error(f"Unregistered chat {event.chat.id}")
                return await event.reply(NOT_REGISTERED_MSG)

        return await handler(event, data)
