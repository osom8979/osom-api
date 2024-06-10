# -*- coding: utf-8 -*-

from io import StringIO
from typing import Awaitable, Callable, Dict, Optional

from overrides import override

from osom_api.arguments import VERBOSE_LEVEL_1
from osom_api.arguments import version as osom_version
from osom_api.commands import EndpointCommands
from osom_api.context.base import BaseContext, BaseContextConfig
from osom_api.exceptions import MsgError
from osom_api.logging.logging import logger
from osom_api.msg import MsgProvider, MsgRequest, MsgResponse
from osom_api.msg.worker import MsgWorker
from osom_api.paths import (
    MQ_BROADCAST_PATH,
    MQ_REGISTER_WORKER_PATH,
    MQ_REGISTER_WORKER_REQUEST_PATH,
    MQ_UNREGISTER_WORKER_PATH,
)
from osom_api.utils.path.mq import encode_path, make_response_path


class CommandCallable:
    def __init__(
        self,
        callback: Callable[[MsgRequest, str], Awaitable[MsgResponse]],
        request_path: Optional[str] = None,
    ):
        self.callback = callback
        self.request_path = request_path if request_path else str()

    @property
    def builtin(self):
        return not self.request_path

    async def __call__(self, request: MsgRequest) -> MsgResponse:
        return await self.callback(request, self.request_path)


class EndpointContext(BaseContext):
    _workers: Dict[str, MsgWorker]
    _commands: Dict[str, CommandCallable]

    def __init__(self, provider: MsgProvider, config: BaseContextConfig):
        super().__init__(
            provider=provider,
            config=config,
            subscribers={
                MQ_BROADCAST_PATH: self.on_broadcast,
                MQ_REGISTER_WORKER_PATH: self.on_register_worker,
                MQ_UNREGISTER_WORKER_PATH: self.on_unregister_worker,
            },
        )

        self._workers = dict()
        self._commands = dict()
        self._commands[EndpointCommands.version] = CommandCallable(self.on_cmd_version)
        self._commands[EndpointCommands.help] = CommandCallable(self.on_cmd_help)

    async def publish_register_worker_request(self) -> None:
        await self._mq.publish(
            key=MQ_REGISTER_WORKER_REQUEST_PATH,
            data=self.provider.encode(),
        )
        logger.info("Published a packet requesting worker information ...")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful in the endpoint context")
        await self.publish_register_worker_request()

    async def on_broadcast(self, data: bytes) -> None:
        pass

    async def on_register_worker(self, data: bytes) -> None:
        try:
            worker = MsgWorker.decode(data)
        except BaseException as e:
            logger.error(e)
            return

        if worker.name in self._workers:
            logger.warning(f"Overwrite and register a new worker: '{worker.name}'")
            self.unregister_worker(worker.name)
        else:
            logger.info(f"Register a new worker: '{worker.name}'")

        self.register_worker(worker)

    async def on_unregister_worker(self, data: bytes) -> None:
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

    def register_worker(self, worker: MsgWorker) -> None:
        self._workers[worker.name] = worker
        for cmd in worker.cmds:
            self._commands[cmd.key] = CommandCallable(self.on_cmd_worker, worker.path)

    def unregister_worker(self, worker_name: str) -> None:
        if worker_name not in self._workers:
            return

        for cmd in self._workers.pop(worker_name).cmds:
            if cmd.key in self._commands:
                self._commands.pop(cmd.key)

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

    async def on_cmd_version(self, request: MsgRequest, path: str) -> MsgResponse:
        assert not path
        return MsgResponse(request.msg_uuid, self.version)

    async def on_cmd_help(self, request: MsgRequest, path: str) -> MsgResponse:
        assert not path
        return MsgResponse(request.msg_uuid, self.help)

    async def on_cmd_worker(self, request: MsgRequest, path: str) -> MsgResponse:
        request_data = request.encode()
        await self._mq.lpush_bytes(path, request_data, expire=30)

        response_path = make_response_path(request.msg_uuid)
        response_datas = await self._mq.brpop_bytes(response_path, timeout=10)

        assert isinstance(response_datas, tuple)
        assert len(response_datas) == 2

        recv_key = response_datas[0]
        recv_data = response_datas[1]
        assert isinstance(recv_key, bytes)
        assert isinstance(recv_data, bytes)
        assert recv_key == encode_path(response_path)

        return MsgResponse.decode(recv_data)

    async def do_message(self, request: MsgRequest) -> Optional[MsgResponse]:
        msg_uuid = request.msg_uuid
        logger.info(f"Msg({msg_uuid}) recv message: " + repr(request))

        if not request.commandable:
            logger.debug(f"Msg({msg_uuid}) is not commandable")
            return None

        coro = self._commands.get(request.command)
        if coro is None:
            logger.warning(f"Msg({msg_uuid}) Unregistered command: {request.command}")
            return None

        if self.verbose >= VERBOSE_LEVEL_1:
            logger.info(f"Msg({msg_uuid}) Run '{request.command}' command")

        try:
            return await coro(request)
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
