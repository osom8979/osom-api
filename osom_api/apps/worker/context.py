# -*- coding: utf-8 -*-

from argparse import Namespace

from overrides import override

from osom_api.aio.run import aio_run
from osom_api.common.config import CommonConfig
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger
from osom_api.mq.path import QUEUE_PATH


class WorkerContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = CommonConfig.from_namespace(args)
        super().__init__(self._config)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    async def start_polling(self) -> None:
        while True:
            logger.debug("Blocking Right POP ...")
            try:
                await self.mq.brpop_bytes(QUEUE_PATH, 10)
            except BaseException as e:
                logger.error(e)

    async def main(self) -> None:
        await self.common_open()
        try:
            logger.debug("Start polling ...")
            await self.start_polling()
        finally:
            await self.common_close()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
