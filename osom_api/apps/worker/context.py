# -*- coding: utf-8 -*-

from argparse import Namespace
from math import floor

from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.worker.config import WorkerConfig
from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.context import Context
from osom_api.exceptions import (
    CommandRuntimeError,
    NoMessageIdError,
    OsomApiError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
)
from osom_api.logging.logging import logger
from osom_api.msg.request import MsgRequest
from osom_api.msg.worker import MsgWorker
from osom_api.paths import (
    MQ_BROADCAST_PATH,
    MQ_REGISTER_WORKER_PATH,
    MQ_REGISTER_WORKER_REQUEST_PATH,
)
from osom_api.utils.path.mq import encode_path, make_response_path
from osom_api.worker.module import Module


class WorkerContext(Context):
    def __init__(self, args: Namespace):
        self._config = WorkerConfig.from_namespace(args)
        self._broadcast_path = encode_path(MQ_BROADCAST_PATH)
        self._register_path = encode_path(MQ_REGISTER_WORKER_REQUEST_PATH)
        subscribe_paths = self._broadcast_path, self._register_path
        super().__init__(config=self._config, subscribe_paths=subscribe_paths)

        self._module = Module(self._config.module_path, self._config.isolate_module)
        self._register = MsgWorker(
            name=self._module.name,
            version=self._module.version,
            doc=self._module.doc,
            path=self._module.path,
            cmds=self._module.cmds,
        )
        self._register_packet = self._register.encode()

    async def publish_register_worker(self) -> None:
        await self.publish(MQ_REGISTER_WORKER_PATH, self._register_packet)
        logger.info("Published register worker packet!")

    @property
    def timeout(self):
        return floor(self._config.redis_blocking_timeout)

    @property
    def expire(self):
        return floor(self._config.redis_expire_medium)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")
        await self.publish_register_worker()

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")
        if self._register_path == channel:
            await self.publish_register_worker()

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

    async def polling_iter(self) -> None:
        packet = await self.mq.brpop_bytes(self._module.path, self.timeout)
        if packet is None:
            raise PollingTimeoutError("Blocking Right POP operation timeout")

        logger.info(f"Received packet: {packet!r}")
        assert isinstance(packet, tuple)
        assert len(packet) == 2
        assert isinstance(packet[0], bytes)
        assert isinstance(packet[1], bytes)

        recv_key = packet[0]
        recv_data = packet[1]
        assert recv_key == encode_path(self._module.path)

        request: MsgRequest
        try:
            request = MsgRequest.decode(recv_data)
        except BaseException as e:
            logger.exception(e)
            raise PacketLoadError("Packet decoding fail") from e

        if not request.msg_uuid:
            raise NoMessageIdError("Message UUID does not exist")

        msg_uuid = request.msg_uuid
        if self._config.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Request[{msg_uuid}] {request.content}")
        else:
            logger.info(f"Request[{msg_uuid}]")

        try:
            result = await self._module.run(request)
        except BaseException as e:
            logger.exception(e)
            raise CommandRuntimeError("A command runtime error was detected") from e

        assert result.msg_uuid == msg_uuid

        try:
            response_packet = result.encode()
            assert isinstance(response_packet, bytes)
        except BaseException as e:
            logger.exception(e)
            raise PacketDumpError("Response packet encoding fail")

        response_path = make_response_path(msg_uuid)
        await self.mq.lpush_bytes(response_path, response_packet, self.expire)

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
