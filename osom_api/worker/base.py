# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import (
    Any,
    Awaitable,
    Callable,
    Dict,
    Iterable,
    NamedTuple,
    Optional,
    Sequence,
    Union,
)

from overrides import override

from osom_api.context import Context
from osom_api.context.mq.path import make_response_path
from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.exceptions import InvalidCommandError
from osom_api.logging.logging import logger
from osom_api.worker.interface import CommandTuple, ParameterTuple, WorkerInterface


@dataclass
class ParameterMeta:
    name: Optional[str] = None
    summary: Optional[str] = None
    default: Any = None


class ReplyFile(NamedTuple):
    name: str
    data: bytes
    content_type: Optional[str] = None


class ReplyTuple(NamedTuple):
    content: Optional[str] = None
    files: Optional[Iterable[ReplyFile]] = None


Reply = Union[
    None,
    str,
    ReplyFile,
    Iterable[ReplyFile],
    ReplyTuple,
    MsgResponse,
]

CommandCallable = Callable[..., Awaitable[Reply]]


@dataclass
class RegisterCommand:
    command: str
    summary: str
    parameters: Dict[str, ParameterTuple]
    callback: CommandCallable

    def as_cmd(self):
        return CommandTuple(
            command=self.command,
            summary=self.summary,
            parameters=list(self.parameters.values()),
        )


class WorkerBase(WorkerInterface):
    _context: Optional[Context]
    _commands: Dict[str, RegisterCommand]

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
    def cmds(self) -> Sequence[CommandTuple]:
        return [cmd.as_cmd() for cmd in self._commands.values()]

    @override
    async def open(self, context) -> None:
        self._context = context

    @override
    async def close(self) -> None:
        self._context = None

    @override
    async def run(self, message: MsgRequest) -> MsgResponse:
        logger.info("Recv message: " + repr(message))

        if not message.is_command():
            raise InvalidCommandError(f"Not a command request: {message.content}")

        msg_cmd = message.parse_command_argument()
        command = msg_cmd.command
        reg_cmd = self._commands.get(command)
        if reg_cmd is None:
            raise InvalidCommandError(f"Unregistered command: {command}")

        kwargs = dict()
        for key, param in reg_cmd.parameters.items():
            kwargs[key] = msg_cmd.get(param.name, param.default)

        await reg_cmd.callback(**kwargs)

        return MsgResponse(message.msg_uuid)

    @property
    def has_context(self) -> bool:
        return self._context is not None

    @property
    def context(self) -> Context:
        assert self._context is not None
        return self._context

    def clear_commands(self) -> None:
        self._commands.clear()

    def register_command(
        self,
        command: str,
        summary: str,
        callback: CommandCallable,
    ) -> None:
        # callback_hints = get_type_hints(callback, include_extras=True)
        self._commands[command] = RegisterCommand(
            command=command,
            summary=summary,
            parameters={},
            callback=callback,
        )
