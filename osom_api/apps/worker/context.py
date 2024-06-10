# -*- coding: utf-8 -*-

from argparse import Namespace
from io import BytesIO
from math import floor
from typing import Iterable

from overrides import override

from osom_api.aio.run import aio_run
from osom_api.apps.worker.config import WorkerConfig
from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.context.base import BaseContext
from osom_api.exceptions import (
    CommandRuntimeError,
    InvalidMessageIdError,
    NoMessageIdError,
    OsomApiError,
    PacketDumpError,
    PacketLoadError,
    PollingTimeoutError,
)
from osom_api.logging.logging import logger
from osom_api.msg import (
    MsgFile,
    MsgFlow,
    MsgProvider,
    MsgRequest,
    MsgResponse,
    MsgStorage,
    MsgWorker,
)
from osom_api.paths import (
    MQ_BROADCAST_PATH,
    MQ_REGISTER_WORKER_PATH,
    MQ_REGISTER_WORKER_REQUEST_PATH,
    MQ_UNREGISTER_WORKER_PATH,
)
from osom_api.utils.path.mq import encode_path
from osom_api.worker.module import Module


class WorkerContext(BaseContext):
    def __init__(self, args: Namespace):
        self._config = WorkerConfig(args)
        super().__init__(
            provider=MsgProvider.worker,
            config=self._config,
            subscribers={
                MQ_BROADCAST_PATH: self.on_broadcast,
                MQ_REGISTER_WORKER_REQUEST_PATH: self.on_register_worker_request,
            },
        )

        self._module = Module(
            self._config.module_path,
            self._config.module_isolate,
            *self._config.opts,
        )
        self._register = MsgWorker(
            name=self._module.name,
            version=self._module.version,
            doc=self._module.doc,
            path=self._module.path,
            cmds=self._module.cmds,
        )
        self._register_packet = self._register.encode()

    async def publish_register_worker(self) -> None:
        await self._mq.publish(MQ_REGISTER_WORKER_PATH, self._register_packet)
        logger.info("Published register worker packet!")

    async def publish_unregister_worker(self) -> None:
        await self._mq.publish(MQ_UNREGISTER_WORKER_PATH, self._module.name.encode())
        logger.info("Published register worker packet!")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful in the Worker context")
        await self.publish_register_worker()

    @override
    async def on_mq_closing(self) -> None:
        logger.warning("Just before closing the Redis task in the Worker context")
        await self.publish_unregister_worker()

    async def on_broadcast(self, data: bytes) -> None:
        pass

    async def on_register_worker_request(self, _: bytes) -> None:
        await self.publish_register_worker()

    async def upload_msg_file(
        self,
        file: MsgFile,
        msg_uuid: str,
        flow: MsgFlow,
        storage=MsgStorage.r2,
    ) -> None:
        if file.content is None:
            raise BufferError("Empty file content")

        await self._s3.upload_data(
            data=BytesIO(file.content),
            key=file.path,
            content_type=file.content_type,
        )
        logger.info(f"Successfully uploaded file to S3: '{file.path}'")

        await self._db.insert_file(
            file_uuid=file.file_uuid,
            provider=file.provider,
            storage=storage,
            name=file.name,
            content_type=file.content_type,
            native_id=file.native_id,
            created_at=file.created_at.isoformat(),
        )
        logger.info(
            "Successfully inserted file info to DB: "
            f"'{file.file_uuid}' -> '{file.path}'"
        )

        await self._db.insert_msg2file(
            msg_uuid=msg_uuid,
            file_uuid=file.file_uuid,
            flow=flow,
        )
        logger.info(
            "Successfully inserted msg2file info to DB: "
            f"'{msg_uuid}' -> {file.file_uuid}"
        )

    async def upload_msg_files(
        self,
        files: Iterable[MsgFile],
        msg_uuid: str,
        flow: MsgFlow,
        storage=MsgStorage.r2,
    ) -> None:
        for file in files:
            await self.upload_msg_file(file, msg_uuid, flow, storage)

    async def upload_msg_request(self, message: MsgRequest) -> None:
        await self._db.insert_msg(
            msg_uuid=message.msg_uuid,
            provider=message.provider,
            message_id=message.message_id,
            channel_id=message.channel_id,
            username=message.username,
            nickname=message.nickname,
            content=message.content,
            created_at=message.created_at.isoformat(),
        )
        logger.info(f"Successfully inserted msg_request to DB: '{message.msg_uuid}'")

        await self.upload_msg_files(
            files=message.files,
            msg_uuid=message.msg_uuid,
            flow=MsgFlow.request,
        )

    async def upload_msg_response(self, message: MsgResponse) -> None:
        await self._db.insert_reply(
            msg=message.msg_uuid,
            content=message.content,
            error=message.error,
            created_at=message.created_at.isoformat(),
        )
        logger.info(f"Successfully inserted msg_response to DB: '{message.msg_uuid}'")

        await self.upload_msg_files(
            files=message.files,
            msg_uuid=message.msg_uuid,
            flow=MsgFlow.response,
        )

    async def open_module(self) -> None:
        logger.debug("Open modules ...")
        await self._module.open(self)
        logger.info("Opened modules")

    async def close_module(self) -> None:
        logger.debug("Close modules ...")
        await self._module.close()
        logger.info("Closed modules")

    async def polling_iter(self) -> None:
        timeout = floor(self._config.redis_blocking_timeout)
        packet = await self._mq.brpop_bytes(self._module.path, timeout)
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

        if self._config.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Request[{request.msg_uuid}] {request.content}")
        else:
            logger.info(f"Request[{request.msg_uuid}]")

        response: MsgResponse
        try:
            response = await self.on_message(request)
        except BaseException as e:
            logger.error(f"Msg({request.msg_uuid}) Request message upload failed: {e}")
            if self._config.debug:
                logger.exception(e)
            response = MsgResponse(request.msg_uuid, error=str(e))

        try:
            response_packet = response.encode()
        except BaseException as e:
            logger.exception(e)
            raise PacketDumpError("Response packet encoding fail")

        assert isinstance(response_packet, bytes)
        response_path = request.get_response_path()

        expire = floor(self._config.redis_expire_medium)
        await self._mq.lpush_bytes(response_path, response_packet, expire)

    async def on_message(self, request: MsgRequest) -> MsgResponse:
        await self.upload_msg_request(request)

        try:
            response = await self._module.run(request)
        except BaseException as e:
            raise CommandRuntimeError("A command runtime error was detected") from e

        await self.upload_msg_response(response)

        if response.msg_uuid != request.msg_uuid:
            raise InvalidMessageIdError(
                "The UUID in the request message and "
                "the UUID in the response message must be the same"
            )

        return response

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
        await self.open_base_context()
        await self.open_module()
        try:
            logger.info("Start polling ...")
            await self.start_polling()
        finally:
            logger.info("Polling is done...")
            await self.close_module()
            await self.close_base_context()

    def run(self) -> None:
        aio_run(self.main(), self._config.use_uvloop)
