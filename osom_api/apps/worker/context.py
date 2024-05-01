# -*- coding: utf-8 -*-

from argparse import Namespace
from math import floor
from typing import Optional

from orjson import dumps, loads
from overrides import override
from type_serialize import serialize

from osom_api.aio.run import aio_run
from osom_api.apps.worker.commands import create_command_map
from osom_api.config import Config
from osom_api.context import Context
from osom_api.exceptions import (
    CommandRuntimeError,
    EmptyApiError,
    NoMessageDataError,
    NoMessageIdError,
    NotFoundCommandKeyError,
    OsomApiError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
)
from osom_api.logging.logging import logger
from osom_api.mq.path import QUEUE_COMMON_PATH, RESPONSE_PATH, encode_path
from osom_api.mq.protocol.worker import (
    WORKER_REQUEST_API_KEY,
    WORKER_REQUEST_DATA_KEY,
    WORKER_REQUEST_MSG_KEY,
)


class WorkerContext(Context):
    def __init__(self, args: Namespace):
        self._config = Config.from_namespace(args)
        super().__init__(self._config)
        self._commands = create_command_map(self)

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
            request = loads(recv_data)
            if not isinstance(request, dict):
                raise TypeError(f"Unsupported request type: {type(request).__name__}")

            request_api = request.get(WORKER_REQUEST_API_KEY)
            request_msg = request.get(WORKER_REQUEST_MSG_KEY)
            request_data = request.get(WORKER_REQUEST_DATA_KEY)
        except BaseException as e:
            logger.exception(e)
            raise PacketLoadError("Packet decoding fail")

        if not request_api:
            raise EmptyApiError("Request worker API is empty")

        command = self._commands.get(request_api)
        if command is None:
            raise NotFoundCommandKeyError("Worker command not found")

        try:
            result = await command.run(request_data)
        except BaseException as e:
            logger.exception(e)
            raise CommandRuntimeError("A command runtime error was detected")

        if not request_msg:
            raise NoMessageIdError("Message ID does not exist")

        if not result:
            raise NoMessageDataError("Message Data does not exist")

        try:
            response_data = dumps(serialize(result))
            assert isinstance(response_data, bytes)
        except BaseException as e:
            logger.exception(e)
            raise PacketDumpError("Packet encoding fail")

        response_path = f"{RESPONSE_PATH}/{request_msg}"
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
            except OsomApiError as e:
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
