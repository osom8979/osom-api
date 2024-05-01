# -*- coding: utf-8 -*-

from argparse import Namespace

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import Message
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.telegram.commands.help import CommandHelp
from osom_api.apps.telegram.commands.version import CommandVersion
from osom_api.apps.telegram.config import TelegramConfig
from osom_api.apps.telegram.middlewares.registration_verifier import (
    RegistrationVerifierMiddleware,
)
from osom_api.arguments import version as osom_version
from osom_api.context import Context
from osom_api.logging.logging import logger


class TelegramContext(Context):
    def __init__(self, args: Namespace):
        self._config = TelegramConfig.from_namespace(args)
        super().__init__(self._config)

        self._bot = Bot(token=self._config.telegram_token)

        self._router = Router()
        self._router.message.outer_middleware.register(
            RegistrationVerifierMiddleware(self.supabase)
        )
        self._router.message.register(self.on_help, CommandHelp())
        self._router.message.register(self.on_version, CommandVersion())
        self._router.message.register(self.on_openai_chat, F.text.startswith("?"))
        self._router.message.register(self.on_fallback)

        self._dispatcher = Dispatcher()
        self._dispatcher.include_routers(self._router)

        self._osom_version = osom_version()

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    async def on_help(self, message: Message) -> None:
        await message.answer(self._osom_version)

    async def on_version(self, message: Message) -> None:
        await message.answer(self._osom_version)

    async def on_openai_chat(self, message: Message) -> None:
        assert message.text
        assert message.text.startswith("?")

        message_text = message.text[1:].strip()
        if not message_text:
            return

        try:
            chat_completion = await self.openai.chat.completions.create(
                messages=[{"role": "user", "content": message_text}],
                model="gpt-4",
            )
            content = chat_completion.choices[0].message.content
            print(chat_completion.model_dump_json())
            # chat_completion_json = chat_completion.model_dump_json()
            await message.reply(content if content else "")
        except BaseException as e:
            message_id = message.message_id
            logger.error(f"Unexpected error occurred in message ({message_id}): {e}")
            await message.reply("Unexpected error occurred")

    async def on_fallback(self, message: Message) -> None:
        assert self
        o = dict(
            event="fallback",
            content_type=message.content_type,
            message_id=message.message_id,
            chat=message.chat.id,
            username=message.chat.username,
            full_name=message.chat.full_name,
            type=message.chat.type,
            text=message.text,
        )
        logger.debug(repr(o))

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._dispatcher.start_polling(self._bot)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
