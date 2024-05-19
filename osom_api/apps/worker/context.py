# -*- coding: utf-8 -*-

from argparse import Namespace
from math import floor

from orjson import dumps, loads
from overrides import override
from type_serialize import serialize

from osom_api.aio.run import aio_run
from osom_api.apps.worker.config import WorkerConfig
from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.context import Context
from osom_api.context.mq.path import encode_path, make_response_path
from osom_api.context.mq.protocol.worker import Keys
from osom_api.exceptions import (
    CommandRuntimeError,
    NoMessageDataError,
    NoMessageIdError,
    OsomApiError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
)
from osom_api.logging.logging import logger
from osom_api.worker.module import Module


class WorkerContext(Context):
    def __init__(self, args: Namespace):
        self._config = WorkerConfig.from_namespace(args)
        super().__init__(self._config)
        self._module = Module(self._config.module_path, self._config.isolate_module)
        self._name = self._module.name
        self._version = self._module.version
        self._doc = self._module.doc
        self._path = self._module.path
        self._cmds = self._module.cmds

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

    async def open_module(self) -> None:
        logger.debug("Open modules ...")
        await self._module.open(self)
        logger.info("Opened modules")

    async def close_module(self) -> None:
        logger.debug("Close modules ...")
        await self._module.close()
        logger.info("Closed modules")

    async def run_module(self, data):
        pass

    async def polling_iter(self) -> None:
        packet = await self.mq.brpop_bytes(self._path, self.timeout)
        if packet is None:
            raise PollingTimeoutError("Blocking Right POP operation timeout")

        logger.info(f"Received packet: {packet!r}")
        assert isinstance(packet, tuple)
        assert len(packet) == 2
        assert isinstance(packet[0], bytes)
        assert isinstance(packet[1], bytes)

        recv_key = packet[0]
        recv_data = packet[1]
        assert recv_key == encode_path(self._path)

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

        assert isinstance(request_id, str)

        if self._config.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Request[{request_id}] {request_data}")
        else:
            logger.info(f"Request[{request_id}]")

        try:
            result = await self.run_module(request_data)
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
        await self.open_module()
        try:
            logger.info("Start polling ...")
            await self.start_polling()
        finally:
            logger.info("Polling is done...")
            await self.close_module()
            await self.close_common_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
