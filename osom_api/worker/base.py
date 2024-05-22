# -*- coding: utf-8 -*-

from dataclasses import dataclass
from inspect import signature
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
    get_type_hints,
)

from overrides import override

from osom_api.context import Context
from osom_api.context.mq.path import make_response_path
from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.exceptions import InvalidCommandError, InvalidParameterError
from osom_api.inspection.bind import assert_parameter_kind_order
from osom_api.logging.logging import logger
from osom_api.worker.interface import CmdTuple, ParamTuple, WorkerInterface


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
    parameters: Dict[str, ParamTuple]
    callback: CommandCallable

    def as_cmd(self):
        return CmdTuple(
            command=self.command,
            doc=self.summary,
            params=list(self.parameters.values()),
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
    def cmds(self) -> Sequence[CmdTuple]:
        return [cmd.as_cmd() for cmd in self._commands.values()]

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

        msg_cmd = request.parse_command_argument()
        command = msg_cmd.command
        reg_cmd = self._commands.get(command)
        if reg_cmd is None:
            raise InvalidCommandError(f"Unregistered command: {command}")

        kwargs = dict()
        for key, param in reg_cmd.parameters.items():
            kwargs[key] = msg_cmd.get(param.key, param.default)

        await reg_cmd.callback(**kwargs)

        return MsgResponse(request.msg_uuid)

    @property
    def has_context(self) -> bool:
        return self._context is not None

    @property
    def context(self) -> Context:
        assert self._context is not None
        return self._context

    def clear_commands(self) -> None:
        self._commands.clear()

    @staticmethod
    def generate_parameters(callback: CommandCallable) -> Dict[str, ParamTuple]:
        hints = get_type_hints(callback, include_extras=True)
        result = dict()
        sig = signature(callback)
        assert_parameter_kind_order(sig)
        for param in sig.parameters.values():
            hint = hints.get(param.name, None)
            meta = getattr(hint, "__metadata__", None) if hint is not None else None

            if meta is not None:
                if not isinstance(meta, ParameterMeta):
                    raise InvalidParameterError(
                        f"Invalid parameter meta type: {type(meta).__name__}"
                    )
                name = meta.name if meta.name else param.name
                summary = meta.summary if meta.summary else str()
                default = meta.default if meta.default is not None else param.default
            else:
                name = param.name
                summary = str()
                default = param.default

            result[name] = ParamTuple(name, summary, default)

        return result

    def register_command(
        self,
        command: str,
        summary: str,
        callback: CommandCallable,
    ) -> None:
        hints = get_type_hints(callback, include_extras=True)
        # return_hint = hints.get("return", None)

        sig = signature(callback)
        assert_parameter_kind_order(sig)

        parameters: Dict[str, ParamTuple] = dict()

        for param in sig.parameters.values():
            hint = hints.get(param.name, None)
            meta = getattr(hint, "__metadata__", None) if hint is not None else None

            if meta is not None:
                if not isinstance(meta, ParameterMeta):
                    raise InvalidParameterError(
                        f"Invalid parameter meta type: {type(meta).__name__}"
                    )
                name = meta.name if meta.name else param.name
                summary = meta.summary if meta.summary else str()
                default = meta.default if meta.default is not None else param.default
            else:
                name = param.name
                summary = str()
                default = param.default

            parameters[name] = ParamTuple(name, summary, default)

        self._commands[command] = RegisterCommand(
            command=command,
            summary=summary,
            parameters={},
            callback=callback,
        )
