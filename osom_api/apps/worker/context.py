# -*- coding: utf-8 -*-

from asyncio.exceptions import CancelledError
from argparse import Namespace

from overrides import override
from type_serialize.json import dumps, loads

from osom_api.aio.run import aio_run
from osom_api.apps.worker.commands.progress.create import ProgressCreate
from osom_api.apps.worker.exceptions import (
    EmptyApiError,
    NoMessageIdError,
    PacketDumpError,
    NotFoundCommandKeyError,
    CommandRuntimeError,
    PacketLoadError,
    PollingTimeoutError,
    WorkerError,
)
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

    async def polling_iter(self) -> None:
        packet = await self.mq.brpop_bytes(QUEUE_PATH, 10)
        if packet is None:
            raise PollingTimeoutError()

        try:
            request = loads(packet[1], WorkerRequest)
            assert isinstance(request, WorkerRequest)
        except BaseException as e:
            raise PacketLoadError() from e

        if request.api:
            raise EmptyApiError()

        command = self._commands.get(request.api)
        if command is None:
            raise NotFoundCommandKeyError()

        try:
            result = await command.run(request.data, self)
        except BaseException as e:
            raise CommandRuntimeError() from e

        if not request.id:
            raise NoMessageIdError()

        response_path = f"{RESPONSE_PATH}/{request.id}"
        try:
            response_data = dumps(result)
            assert isinstance(response_data, bytes)
        except BaseException as e:
            raise PacketDumpError() from e

        await self.mq.lpush_bytes(response_path, response_data)

    async def start_polling(self) -> None:
        while True:
            try:
                await self.polling_iter()
            except WorkerError as e:
                continue
            except CancelledError:
                logger.warning("A Cancel signal was detected.")
                break
            except BaseException as e:
                logger.exception(e)
                break

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
