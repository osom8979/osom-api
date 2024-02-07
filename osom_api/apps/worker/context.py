# -*- coding: utf-8 -*-

from argparse import Namespace
from math import floor
from typing import Dict, Optional

from overrides import override
from type_serialize.json import dumps, loads

from osom_api.aio.run import aio_run
from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.apps.worker.commands.progress.create import ProgressCreate
from osom_api.apps.worker.exceptions import (
    CommandRuntimeError,
    EmptyApiError,
    NoMessageIdError,
    NotFoundCommandKeyError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
    WorkerError,
)
from osom_api.common.config import CommonConfig
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger
from osom_api.mq.path import QUEUE_COMMON_PATH, RESPONSE_PATH, encode_path
from osom_api.mq.protocol.worker import WorkerRequest


class WorkerContext(CommonContext):
    _commands: Dict[str, WorkerCommand]

    def __init__(self, args: Namespace, task_name: Optional[str] = None):
        self._config = CommonConfig.from_namespace(args)
        self._task_name = task_name if task_name else self.__class__.__name__
        super().__init__(self._config)

        commands = (ProgressCreate,)
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

    async def polling_iter(
        self,
        timeout: Optional[int] = None,
        expire: Optional[int] = None,
    ) -> None:
        packet = await self.mq.brpop_bytes(QUEUE_COMMON_PATH, timeout)
        if packet is None:
            raise PollingTimeoutError("Blocking Right POP operation timeout")

        logger.info(f"Received packet: {packet!r}")
        assert isinstance(packet, tuple)
        assert len(packet) == 2
        assert isinstance(packet[0], bytes)
        assert isinstance(packet[1], bytes)

        recv_key = packet[0]
        recv_data = packet[1]
        assert recv_key == encode_path(QUEUE_COMMON_PATH)

        try:
            request = loads(recv_data, WorkerRequest)
            assert isinstance(request, WorkerRequest)
        except BaseException as e:
            raise PacketLoadError("Packet decoding fail") from e

        if not request.api:
            raise EmptyApiError("Request worker API is empty")

        command = self._commands.get(request.api)
        if command is None:
            raise NotFoundCommandKeyError("Worker command not found")

        try:
            result = await command.run(request.data, self)
        except BaseException as e:
            raise CommandRuntimeError("A command runtime error was detected") from e

        if not request.id:
            raise NoMessageIdError("Message ID does not exist")

        try:
            response_data = dumps(result)
            assert isinstance(response_data, bytes)
        except BaseException as e:
            raise PacketDumpError("Packet encoding fail") from e

        response_path = f"{RESPONSE_PATH}/{request.id}"
        await self.mq.lpush_bytes(response_path, response_data, expire)

    async def start_polling(self) -> None:
        while True:
            try:
                timeout_seconds = floor(self._config.redis_blocking_timeout)
                expire_seconds = floor(self._config.redis_expire_medium)
                await self.polling_iter(timeout_seconds, expire_seconds)
            except NoMessageIdError:
                pass
            except CommandRuntimeError as e:
                logger.error(e)
            except WorkerError as e:
                logger.debug(e)

    async def main(self) -> None:
        await self.open_common_context()
        try:
            logger.info("Start polling ...")
            await self.start_polling()
        finally:
            logger.info("Polling is done...")
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
