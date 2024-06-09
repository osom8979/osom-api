# -*- coding: utf-8 -*-

from argparse import Namespace

from aiogram import Bot, Dispatcher, Router
from aiogram.enums.content_type import ContentType
from aiogram.types import Message

from osom_api.aio.run import aio_run
from osom_api.apps.telegram.config import TelegramConfig
from osom_api.apps.telegram.middlewares.registration_verifier import (
    RegistrationVerifierMiddleware,
)
from osom_api.context.endpoint import EndpointContext
from osom_api.msg import MsgFile, MsgProvider, MsgRequest


class TelegramContext(EndpointContext):
    def __init__(self, args: Namespace):
        self._config = TelegramConfig(args)
        super().__init__(MsgProvider.telegram, self._config)

        self._bot = Bot(token=self._config.telegram_token)

        self._router = Router()
        self._router.message.outer_middleware.register(
            RegistrationVerifierMiddleware(self.db)
        )
        self._router.message.register(self.on_message)

        self._dispatcher = Dispatcher()
        self._dispatcher.include_routers(self._router)

    async def on_message(self, message: Message) -> None:
        files = list()

        if message.photo is not None:
            assert message.content_type == ContentType.PHOTO
            file_sizes = [p.file_size if p.file_size else 0 for p in message.photo]
            largest_file_index = file_sizes.index(max(file_sizes))
            photo = message.photo[largest_file_index]
            file_info = await self._bot.get_file(photo.file_id)
            assert file_info.file_path
            file_buffer = await self._bot.download_file(file_info.file_path)
            assert file_buffer is not None
            file_content = file_buffer.read()
            msg_file = MsgFile(
                provider=MsgProvider.telegram,
                native_id=photo.file_id,
                name=file_info.file_path,
                content=file_content,
                content_type="image/jpeg",
                width=photo.width,
                height=photo.height,
                created_at=message.date,
            )
            files.append(msg_file)

        from_user = message.from_user
        username = from_user.username if from_user is not None else None
        full_name = from_user.full_name if from_user is not None else None

        if message.content_type == ContentType.TEXT and message.text:
            msg_content = message.text
        elif message.content_type == ContentType.PHOTO and message.caption:
            msg_content = message.caption
        else:
            msg_content = str()

        msg = MsgRequest(
            provider=MsgProvider.telegram,
            message_id=message.message_id,
            channel_id=message.chat.id,
            content=msg_content,
            username=username,
            nickname=full_name,
            files=files,
            created_at=message.date,
        )

        response = await self.do_message(msg)
        if response is None:
            return

        await message.reply(response.reply_content)

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._dispatcher.start_polling(self._bot)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
