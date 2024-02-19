# -*- coding: utf-8 -*-

# fmt: off
# isort: off
from osom_api.packages.helper.aiogramlib import Bot, Router, Dispatcher
# isort: on
# fmt: on

from argparse import Namespace

from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.utils.markdown import hbold
from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.telegram.commands.help import CommandHelp
from osom_api.apps.telegram.commands.version import CommandVersion
from osom_api.apps.telegram.config import TelegramConfig
from osom_api.arguments import version as osom_version
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger


class TelegramContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = TelegramConfig.from_namespace(args)
        super().__init__(self._config)

        self._bot = Bot(
            token=self._config.telegram_token,
            parse_mode=ParseMode.HTML,
        )

        self._router = Router()
        self._router.message.register(self.on_help, CommandHelp())
        self._router.message.register(self.on_version, CommandVersion())

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
        await message.answer(hbold(self._osom_version))

    async def main(self) -> None:
        await self.open_common_context()
        try:
            await self._dispatcher.start_polling(self._bot)
        finally:
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
