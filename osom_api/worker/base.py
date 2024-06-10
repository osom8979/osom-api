# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from overrides import override

from osom_api.context.base import BaseContext
from osom_api.exceptions import InvalidCommandError, InvalidContextError
from osom_api.logging.logging import logger
from osom_api.msg import MsgRequest, MsgResponse
from osom_api.utils.path.mq import make_request_path
from osom_api.worker.command import DEFAULT_KEY_PREFIX, CommandCallable, WorkerCommand
from osom_api.worker.descs import CmdDesc
from osom_api.worker.interface import WorkerInterface


class WorkerBase(WorkerInterface):
    _context: Optional[BaseContext]
    _commands: Dict[str, WorkerCommand]

    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        docs: Optional[str] = None,
        path: Optional[str] = None,
    ):
        self._name = name if name else str()
        self._version = version if version else str()
        self._docs = docs if docs else str()
        self._path = path if path else make_request_path(self._name)
        self._commands = dict()
        self._context = None

    @property
    @override
    def name(self) -> str:
        return self._name

    @property
    @override
    def version(self) -> str:
        return self._version

    @property
    @override
    def doc(self) -> str:
        return self._docs

    @property
    @override
    def path(self) -> str:
        return self._path

    @property
    @override
    def cmds(self) -> List[CmdDesc]:
        return list(cmd.as_desc() for cmd in self._commands.values())

    @override
    def init(self, *args) -> None:
        logger.debug(f"Initialize the worker module: {args}")

    @override
    async def open(self, context) -> None:
        logger.warning("Open the worker module")
        self._context = context
        if self._context is None:
            raise InvalidContextError("No context provided")

    @override
    async def close(self) -> None:
        logger.warning("Close the worker module")
        self._context = None

    @override
    async def run(self, request: MsgRequest) -> MsgResponse:
        logger.info("Recv message: " + repr(request))

        if not request.commandable:
            raise InvalidCommandError(f"Not a command request: {request.content}")

        reg_cmd = self._commands.get(request.command)
        if reg_cmd is None:
            raise InvalidCommandError(f"Unregistered command: {request.command}")

        return await reg_cmd(request)

    @property
    def has_context(self) -> bool:
        return self._context is not None

    @property
    def context(self) -> BaseContext:
        assert self._context is not None
        return self._context

    @property
    def provider(self):
        return self.context.provider

    @property
    def command_prefix(self):
        return self.context.command_prefix

    @property
    def verbose(self) -> int:
        return self.context.verbose

    @property
    def debug(self) -> bool:
        return self.context.debug

    def register_command(
        self,
        callback: CommandCallable,
        prefix: Optional[str] = DEFAULT_KEY_PREFIX,
    ) -> None:
        cmd = WorkerCommand.from_callback(callback, prefix)
        self._commands[cmd.key] = cmd
