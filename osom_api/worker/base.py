# -*- coding: utf-8 -*-

from typing import Dict, List, Optional

from overrides import override

from osom_api.context import Context
from osom_api.context.mq.path import make_response_path
from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.exceptions import InvalidCommandError
from osom_api.logging.logging import logger
from osom_api.worker.command import DEFAULT_KEY_PREFIX, CommandCallable, WorkerCommand
from osom_api.worker.descs import CmdDesc
from osom_api.worker.interface import WorkerInterface


class WorkerBase(WorkerInterface):
    _context: Optional[Context]
    _commands: Dict[str, WorkerCommand]

    def __init__(
        self,
        name: Optional[str] = None,
        version: Optional[str] = None,
        docs: Optional[str] = None,
        path: Optional[str] = None,
        *args,
        **kwargs,
    ):
        self._name = name if name else str()
        self._version = version if version else str()
        self._docs = docs if docs else str()
        self._path = path if path else make_response_path(self._name)

        self.args = list(args)
        self.kwargs = dict(**kwargs)

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
    async def open(self, context) -> None:
        self._context = context

    @override
    async def close(self) -> None:
        self._context = None

    @override
    async def run(self, request: MsgRequest) -> MsgResponse:
        logger.info("Recv message: " + repr(request))

        if not request.is_command():
            raise InvalidCommandError(f"Not a command request: {request.content}")

        command = request.command
        reg_cmd = self._commands.get(command)
        if reg_cmd is None:
            raise InvalidCommandError(f"Unregistered command: {command}")

        return await reg_cmd(request)

    @property
    def has_context(self) -> bool:
        return self._context is not None

    @property
    def context(self) -> Context:
        assert self._context is not None
        return self._context

    def register_command(
        self,
        callback: CommandCallable,
        prefix: Optional[str] = DEFAULT_KEY_PREFIX,
    ) -> None:
        cmd = WorkerCommand.from_callback(callback, prefix)
        self._commands[cmd.key] = cmd
