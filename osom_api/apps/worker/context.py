# -*- coding: utf-8 -*-

from argparse import Namespace
from math import floor

from orjson import dumps, loads
from overrides import override
from type_serialize import serialize

from osom_api.aio.run import aio_run
from osom_api.apps.worker.config import WorkerConfig
from osom_api.context import Context
from osom_api.context.mq.path import QUEUE_COMMON_PATH, encode_path, make_response_path
from osom_api.context.mq.protocol.worker import Keys
from osom_api.exceptions import (
    CommandRuntimeError,
    EmptyApiError,
    InvalidCommandError,
    NoMessageDataError,
    NoMessageIdError,
    OsomApiError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
)
from osom_api.logging.logging import logger


class WorkerContext(Context):
    def __init__(self, args: Namespace):
        self._config = WorkerConfig.from_namespace(args)
        super().__init__(self._config)

    @property
    def request_path(self):
        if self._config.request_path:
            return self._config.request_path
        else:
            return QUEUE_COMMON_PATH

    @property
    def module_path(self):
        if self._config.module_path:
            return self._config.module_path
        else:
            return QUEUE_COMMON_PATH

    @property
    def timeout(self):
        return floor(self._config.redis_blocking_timeout)

    @property
    def expire(self):
        return floor(self._config.redis_expire_medium)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    async def open_modules(self) -> None:
        logger.debug("Open modules ...")
        logger.info("Opened modules")

    async def close_modules(self) -> None:
        logger.debug("Close modules ...")
        logger.info("Closed modules")

    async def polling_iter(self) -> None:
        packet = await self.mq.brpop_bytes(self.request_path, self.timeout)
        if packet is None:
            raise PollingTimeoutError("Blocking Right POP operation timeout")

        logger.info(f"Received packet: {packet!r}")
        assert isinstance(packet, tuple)
        assert len(packet) == 2
        assert isinstance(packet[0], bytes)
        assert isinstance(packet[1], bytes)

        recv_key = packet[0]
        recv_data = packet[1]
        assert recv_key == encode_path(self.request_path)

        try:
            request = loads(recv_data)
            if not isinstance(request, dict):
                raise TypeError(f"Unsupported request type: {type(request).__name__}")

            request_id = request.get(Keys.id)
            request_data = request.get(Keys.data)
        except BaseException as e:
            logger.exception(e)
            raise PacketLoadError("Packet decoding fail")

        if not request_id:
            raise NoMessageIdError("Message ID does not exist")

        try:
            # result = await worker_command.run(request_data)
            result = None
        except BaseException as e:
            logger.exception(e)
            raise CommandRuntimeError("A command runtime error was detected")

        if not result:
            raise NoMessageDataError("Message Data does not exist")

        try:
            response_data = dumps(serialize(result))
            assert isinstance(response_data, bytes)
        except BaseException as e:
            logger.exception(e)
            raise PacketDumpError("Response packet encoding fail")

        response_path = make_response_path(request_id)
        await self.mq.lpush_bytes(response_path, response_data, self.expire)

    async def start_polling(self) -> None:
        while True:
            try:
                await self.polling_iter()
            except NoMessageIdError:
                pass
            except CommandRuntimeError as e:
                logger.error(e)
            except OsomApiError as e:
                logger.debug(e)

    async def main(self) -> None:
        await self.open_common_context()
        await self.open_modules()
        try:
            logger.info("Start polling ...")
            await self.start_polling()
        finally:
            logger.info("Polling is done...")
            await self.close_modules()
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
