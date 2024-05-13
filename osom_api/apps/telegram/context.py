# -*- coding: utf-8 -*-

from argparse import Namespace

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.telegram.config import TelegramConfig
from osom_api.apps.telegram.middlewares.registration_verifier import (
    RegistrationVerifierMiddleware,
)
from osom_api.context import Context
from osom_api.context.msg import MsgFile, MsgProvider, MsgRequest
from osom_api.logging.logging import logger


class HelpCommand(Command):
    def __init__(self):
        super().__init__("help")


class VersionCommand(Command):
    def __init__(self):
        super().__init__("version")


class TelegramContext(Context):
    def __init__(self, args: Namespace):
        self._config = TelegramConfig.from_namespace(args)
        super().__init__(self._config)

        self._bot = Bot(token=self._config.telegram_token)

        self._router = Router()
        self._router.message.outer_middleware.register(
            RegistrationVerifierMiddleware(self.db)
        )
        self._router.message.register(self.on_help, HelpCommand())
        self._router.message.register(self.on_version, VersionCommand())
        self._router.message.register(self.on_message)

        self._dispatcher = Dispatcher()
        self._dispatcher.include_routers(self._router)

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
        await message.answer(self.help)

    async def on_version(self, message: Message) -> None:
        await message.answer(self.version)

    async def on_message(self, message: Message) -> None:
        files = list()
        if message.photo is not None:
            file_sizes = [p.file_size if p.file_size else 0 for p in message.photo]
            largest_file_index = file_sizes.index(max(file_sizes))
            photo = message.photo[largest_file_index]
            file_info = await self._bot.get_file(photo.file_id)
            assert file_info.file_path
            file_buffer = await self._bot.download_file(file_info.file_path)
            assert file_buffer is not None
            content = file_buffer.read()
            msg_file = MsgFile(
                content_type="image/jpeg",
                file_id=photo.file_id,
                file_name=file_info.file_path,
                file_size=photo.file_size if photo.file_size else 0,
                image_width=photo.width,
                image_height=photo.height,
                content=content,
            )
            files.append(msg_file)

        chat = message.chat
        username = chat.username if chat.username else str()
        text = message.text if message.text else str()
        msg = MsgRequest(
            provider=MsgProvider.Telegram,
            message_id=message.message_id,
            channel_id=chat.id,
            username=username,
            nickname=chat.full_name,
            text=text,
            created_at=message.date,
            files=files,
        )

        response = await self.do_message(msg)
        if response is None:
            return

        if not response.text:
            return

        await message.reply(response.text)

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._dispatcher.start_polling(self._bot)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
