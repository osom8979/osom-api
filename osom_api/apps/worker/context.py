# -*- coding: utf-8 -*-

from argparse import Namespace

from overrides import override
from type_serialize.json import dumps, loads

from osom_api.aio.run import aio_run
from osom_api.apps.worker.commands.progress.create import ProgressCreate
from osom_api.common.config import CommonConfig
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger
from osom_api.mq.path import QUEUE_PATH, RESPONSE_PATH
from osom_api.mq.protocol.worker import WorkerRequest


class WorkerContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = CommonConfig.from_namespace(args)
        super().__init__(self._config)

        commands = {ProgressCreate}
        self._commands = {c.__api__: c() for c in commands}

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
            packet = await self.mq.brpop_bytes(QUEUE_PATH, 10)
            if packet is None:
                continue

            request = loads(packet[1], WorkerRequest)
            assert isinstance(request, WorkerRequest)
            message_api = request.api
            message_id = request.id
            message_data = request.data

            command = self._commands.get(message_api)
            if command is None:
                continue

            result = await command.run(message_data, self)
            if message_id:
                response_path = f"{RESPONSE_PATH}/{message_id}"
                response_data = dumps(result)
                await self.mq.lpush_bytes(response_path, response_data)

    async def main(self) -> None:
        await self.common_open()
        try:
            logger.info("Start polling ...")
            await self.start_polling()
        finally:
            logger.info("Polling is done...")
            await self.common_close()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
