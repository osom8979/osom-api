# -*- coding: utf-8 -*-

from dataclasses import dataclass
from inspect import Parameter, signature
from typing import Awaitable, Callable, Dict, Optional, Sequence

from overrides import override

from osom_api.context import Context
from osom_api.context.mq.path import make_response_path
from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.exceptions import InvalidCommandError
from osom_api.inspection.bind import assert_parameter_kind_order
from osom_api.logging.logging import logger
from osom_api.worker.descs import CmdDesc, ParamDesc
from osom_api.worker.interface import WorkerInterface
from osom_api.worker.metas import AnnotatedMeta, NoDefault, ParamMeta
from osom_api.worker.replys import Reply

CommandCallable = Callable[..., Awaitable[Reply]]


def make_parameter_desc(param: Parameter) -> ParamDesc:
    name = param.name
    metadata = getattr(param.annotation, "__metadata__", None)
    default = param.default if param.default != param.empty else None
    summary = str()

    if metadata is not None:
        assert isinstance(metadata, tuple)
        for meta in metadata:
            if not isinstance(meta, AnnotatedMeta):
                continue

            if isinstance(meta, ParamMeta):
                if meta.name is not None:
                    name = meta.name
                if meta.summary is not None:
                    summary = meta.summary
                if meta.default != NoDefault:
                    default = meta.default

    return ParamDesc(name, summary, default)


def make_parameter_desc_map(callback: CommandCallable) -> Dict[str, ParamDesc]:
    sig = signature(callback)
    assert_parameter_kind_order(sig)
    return {p.name: make_parameter_desc(p) for p in sig.parameters.values()}


@dataclass
class _RegisterCommand:
    command: str
    summary: str
    parameters: Dict[str, ParamDesc]
    callback: CommandCallable

    def as_cmd(self):
        return CmdDesc(
            key=self.command,
            doc=self.summary,
            params=list(self.parameters.values()),
        )


class WorkerBase(WorkerInterface):
    _context: Optional[Context]
    _commands: Dict[str, _RegisterCommand]

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
    def cmds(self) -> Sequence[CmdDesc]:
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

    def register_command(
        self,
        callback: CommandCallable,
        *,
        command: Optional[str] = None,
        summary: Optional[str] = None,
    ) -> None:
        command = command if command is not None else callback.__name__
        summary = summary if summary is not None else callback.__doc__
        assert command is not None
        assert summary is not None
        self._commands[command] = _RegisterCommand(
            command=command,
            summary=summary,
            parameters=make_parameter_desc_map(callback),
            callback=callback,
        )
