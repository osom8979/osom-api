# -*- coding: utf-8 -*-

from io import StringIO
from typing import Awaitable, Callable, Dict, Optional

from overrides import override

from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.arguments import version as osom_version
from osom_api.commands import EndpointCommands
from osom_api.config import Config
from osom_api.context import Context
from osom_api.context.mq.path import encode_path
from osom_api.context.mq.protocols.worker import RegisterWorker
from osom_api.exceptions import MsgError
from osom_api.logging.logging import logger
from osom_api.mq_paths import (
    BROADCAST_PATH,
    REGISTER_WORKER_PATH,
    REGISTER_WORKER_REQUEST_PATH,
)
from osom_api.msg import MsgProvider, MsgRequest, MsgResponse


class EndpointContext(Context):
    _commands: Dict[str, Callable[[MsgRequest], Awaitable[MsgResponse]]]
    _workers: Dict[str, RegisterWorker]

    def __init__(self, config: Config):
        self._broadcast_path = encode_path(BROADCAST_PATH)
        self._register_worker_path = encode_path(REGISTER_WORKER_PATH)
        subscribe_paths = self._broadcast_path, self._register_worker_path
        super().__init__(config=config, subscribe_paths=subscribe_paths)

        self._commands = dict()
        self._commands[EndpointCommands.version] = self.on_cmd_version
        self._commands[EndpointCommands.help] = self.on_cmd_help
        self._workers = dict()

    async def publish_register_worker_request(self) -> None:
        await self.publish(REGISTER_WORKER_REQUEST_PATH, MsgProvider.telegram.encode())
        logger.info("Published register worker request packet!")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")
        await self.publish_register_worker_request()

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")
        if self._register_worker_path == channel:
            info = RegisterWorker.decode(data)
            self._workers[info.name] = info

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    @property
    def version(self):
        return osom_version()

    @property
    def help(self):
        version_command = self.command_prefix + EndpointCommands.version
        help_command = self.command_prefix + EndpointCommands.help

        buffer = StringIO()
        buffer.write("Available commands:\n")
        buffer.write(f"{version_command} - Show help message\n")
        buffer.write(f"{help_command} - Show version number\n")

        for worker in self._workers.values():
            buffer.write(worker.as_help(self.command_prefix))

        return buffer.getvalue()

    async def on_cmd_version(self, request: MsgRequest) -> MsgResponse:
        return MsgResponse(request.msg_uuid, self.version)

    async def on_cmd_help(self, request: MsgRequest) -> MsgResponse:
        return MsgResponse(request.msg_uuid, self.help)

    async def do_message(self, request: MsgRequest) -> Optional[MsgResponse]:
        msg_uuid = request.msg_uuid
        logger.info("Do message: " + repr(request))

        if not request.commandable:
            return None

        command = request.command
        coro = self._commands.get(command)
        if coro is None:
            logger.warning(f"Msg({msg_uuid}) Unregistered command: {command}")
            return None

        if self.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Msg({msg_uuid}) Run '{command}' command")

        try:
            await self.upload_msg_request(request)
        except BaseException as e:
            logger.error(f"Msg({msg_uuid}) Request message upload failed: {e}")
            if self.debug:
                logger.exception(e)
            return MsgResponse(msg_uuid, error=str(e))

        try:
            return await coro(request)
        except MsgError as e:
            logger.error(f"Msg({e.msg_uuid}) {e}")
            if self.debug and self.verbose >= VERBOSE_LEVEL_1:
                logger.exception(e)
            return MsgResponse(e.msg_uuid, str(e))
        except BaseException as e:
            logger.error(f"Msg({msg_uuid}) Unexpected error occurred: {e}")
            if self.debug:
                logger.exception(e)
            return None
