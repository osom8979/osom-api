# -*- coding: utf-8 -*-

from io import StringIO
from typing import Awaitable, Callable, Dict, Optional

from overrides import override

from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.arguments import version as osom_version
from osom_api.commands import EndpointCommands
from osom_api.config import Config
from osom_api.context import Context
from osom_api.context.mq.protocols.worker import RegisterWorker
from osom_api.exceptions import MsgError
from osom_api.logging.logging import logger
from osom_api.msg import MsgProvider, MsgRequest, MsgResponse
from osom_api.paths import (
    MQ_BROADCAST_PATH,
    MQ_REGISTER_WORKER_PATH,
    MQ_REGISTER_WORKER_REQUEST_PATH,
    MQ_UNREGISTER_WORKER_PATH,
)
from osom_api.utils.path.mq import encode_path


class CommandCallable:
    def __init__(
        self,
        callback: Callable[[MsgRequest, str], Awaitable[MsgResponse]],
        request_path: Optional[str] = None,
    ):
        self.callback = callback
        self.request_path = request_path if request_path else str()

    async def __call__(self, request: MsgRequest) -> MsgResponse:
        return await self.callback(request, self.request_path)


class EndpointContext(Context):
    _commands: Dict[str, CommandCallable]
    _workers: Dict[str, RegisterWorker]

    def __init__(self, provider: MsgProvider, config: Config):
        self._broadcast_path = encode_path(MQ_BROADCAST_PATH)
        self._register_worker_path = encode_path(MQ_REGISTER_WORKER_PATH)
        self._unregister_worker_path = encode_path(MQ_UNREGISTER_WORKER_PATH)
        subscribe_paths = (
            self._broadcast_path,
            self._register_worker_path,
            self._unregister_worker_path,
        )
        super().__init__(config=config, subscribe_paths=subscribe_paths)

        self._provider = provider
        self._commands = dict()
        self._commands[EndpointCommands.version] = CommandCallable(self._cmd_version)
        self._commands[EndpointCommands.help] = CommandCallable(self._cmd_help)
        self._workers = dict()

    def register_worker(self, worker: RegisterWorker) -> None:
        self._workers[worker.name] = worker
        for cmd in worker.cmds:
            self._commands[cmd.key] = CommandCallable(self._cmd_worker, worker.path)

    def unregister_worker(self, worker_name: str) -> None:
        if worker_name not in self._workers:
            return

        for cmd in self._workers.pop(worker_name).cmds:
            if cmd.key in self._commands:
                self._commands.pop(cmd.key)

    async def publish_register_worker_request(self) -> None:
        await self.publish(
            key=MQ_REGISTER_WORKER_REQUEST_PATH,
            data=self._provider.encode(),
        )
        logger.info("Published register worker request packet!")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")
        await self.publish_register_worker_request()

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv subscribed message: {channel!r} -> {data!r}")

        match channel:
            case self._register_worker_path:
                self.on_register_worker(data)
            case self._unregister_worker_path:
                self.on_unregister_worker(data)
            case _:
                pass

    def on_register_worker(self, data: bytes) -> None:
        try:
            worker = RegisterWorker.decode(data)
        except BaseException as e:
            logger.error(e)
            return

        if worker.name in self._workers:
            logger.warning(
                f"Register worker: '{worker.name}'"
                " (It already exists. Overwrite with new worker)"
            )
            self.unregister_worker(worker.name)
        else:
            logger.info(f"Register worker: '{worker.name}'")

        self.register_worker(worker)

    def on_unregister_worker(self, data: bytes) -> None:
        try:
            name = str(data, encoding="utf-8")
        except BaseException as e:
            logger.error(e)
            return

        if name in self._workers:
            logger.info(f"Unregister worker: '{name}'")
            self.unregister_worker(name)
        else:
            logger.warning(f"Unregister worker: '{name}' (but does not exist)")

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

    async def _cmd_version(self, request: MsgRequest, path: str) -> MsgResponse:
        assert not path
        return MsgResponse(request.msg_uuid, self.version)

    async def _cmd_help(self, request: MsgRequest, path: str) -> MsgResponse:
        assert not path
        return MsgResponse(request.msg_uuid, self.help)

    async def _cmd_worker(self, request: MsgRequest, path: str) -> MsgResponse:
        return await self.request_command(path, request)

    async def do_message(self, request: MsgRequest) -> Optional[MsgResponse]:
        msg_uuid = request.msg_uuid
        logger.info(f"Msg({msg_uuid}) Recv message: " + repr(request))

        if not request.commandable:
            logger.debug(f"Msg({msg_uuid}) is not commandable")
            return None

        cmd_callable = self._commands.get(request.command)
        if cmd_callable is None:
            logger.warning(f"Msg({msg_uuid}) Unregistered command: {request.command}")
            return None

        if self.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Msg({msg_uuid}) Run '{request.command}' command")

        try:
            await self.upload_msg_request(request)
        except BaseException as e:
            logger.error(f"Msg({msg_uuid}) Request message upload failed: {e}")
            if self.debug:
                logger.exception(e)
            return MsgResponse(msg_uuid, error=str(e))

        try:
            return await cmd_callable(request)
        except MsgError as e:
            logger.error(f"Msg({e.msg_uuid}) {e}")
            if self.debug and self.verbose >= VERBOSE_LEVEL_1:
                logger.exception(e)
            return MsgResponse(e.msg_uuid, error=str(e))
        except BaseException as e:
            logger.error(f"Msg({msg_uuid}) Unexpected error occurred: {e}")
            if self.debug:
                logger.exception(e)
            return None
