# -*- coding: utf-8 -*-

from argparse import Namespace

from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.bot.config import BotConfig
from osom_api.arguments import version as osom_version
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger


class BotContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = BotConfig.from_namespace(args)
        super().__init__(self._config)

        self._osom_version = osom_version()

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.info("The Redis subscription task is completed")

    async def main(self) -> None:
        await self.common_open()
        try:
            # TODO: ...
            pass
        finally:
            await self.common_close()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
