# -*- coding: utf-8 -*-

from argparse import Namespace

from aiogram import Bot, Dispatcher, Router
from aiogram.enums.content_type import ContentType
from aiogram.types import Message
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.telegram.config import TelegramConfig
from osom_api.apps.telegram.middlewares.registration_verifier import (
    RegistrationVerifierMiddleware,
)
from osom_api.context import Context
from osom_api.context.mq.path import encode_path
from osom_api.context.mq.protocols.worker import RegisterWorker
from osom_api.context.msg import MsgFile, MsgProvider, MsgRequest
from osom_api.logging.logging import logger
from osom_api.mq_paths import (
    BROADCAST_PATH,
    REGISTER_WORKER_PATH,
    REGISTER_WORKER_REQUEST_PATH,
)


class TelegramContext(Context):
    def __init__(self, args: Namespace):
        self._config = TelegramConfig.from_namespace(args)
        self._broadcast_path = encode_path(BROADCAST_PATH)
        self._register_worker_path = encode_path(REGISTER_WORKER_PATH)
        subscribe_paths = self._broadcast_path, self._register_worker_path
        super().__init__(config=self._config, subscribe_paths=subscribe_paths)

        self._bot = Bot(token=self._config.telegram_token)

        self._router = Router()
        self._router.message.outer_middleware.register(
            RegistrationVerifierMiddleware(self.db)
        )
        self._router.message.register(self.on_message)

        self._dispatcher = Dispatcher()
        self._dispatcher.include_routers(self._router)

    async def publish_register_worker_request(self) -> None:
        await self.publish(REGISTER_WORKER_REQUEST_PATH, MsgProvider.telegram.encode())
        logger.info("Published register worker request packet!")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")
        await self.publish_register_worker_request()

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")
        if self._register_worker_path == channel:
            worker_info = RegisterWorker.decode(data)

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

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
