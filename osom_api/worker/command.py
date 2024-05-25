# -*- coding: utf-8 -*-

from inspect import Parameter, signature
from typing import Any, Awaitable, Callable, Dict, Final, Optional, get_type_hints

from osom_api.chrono.datetime import tznow
from osom_api.context.msg import MsgCmd, MsgRequest, MsgResponse
from osom_api.exceptions import CommandRuntimeError, InvalidCommandError
from osom_api.logging.logging import logger
from osom_api.worker.descs import CmdDesc, ParamDesc
from osom_api.worker.metas import AnnotatedMeta, ParamMeta
from osom_api.worker.params import (
    ContentParam,
    CreatedAtParam,
    FileParam,
    FilesParam,
    MsgUUIDParam,
    NicknameParam,
    Param,
    UsernameParam,
)
from osom_api.worker.replys import (
    ContentReply,
    FileReply,
    FilesReply,
    Reply,
    ReplyTuple,
)
from osom_api.worker.values import NoDefault

CommandCallable = Callable[..., Awaitable[Reply]]

DEFAULT_KEY_PREFIX: Final[str] = "on_"

SUPPORTED_PARAMETER_KINDS = Parameter.POSITIONAL_OR_KEYWORD, Parameter.VAR_POSITIONAL
RUNTIME_REQUEST_TYPES = Param, MsgRequest


def make_parameter_desc(param: Parameter) -> ParamDesc:
    # if isinstance(param.annotation, type):
    #     origin = param.annotation
    # else:
    #     # isinstance(param.annotation, typing._AnnotatedAlias)
    #     origin = getattr(param.annotation, "__origin__", None)
    #
    # if (
    #     origin is not None
    #     and isinstance(origin, type)
    #     and issubclass(origin, RUNTIME_REQUEST_TYPES)
    # ):
    #     return None

    name = param.name
    summary = str()
    metadata = getattr(param.annotation, "__metadata__", None)
    default = param.default if param.default != param.empty else None

    if metadata is not None:
        assert isinstance(metadata, tuple)
        for meta in metadata:
            if not isinstance(meta, AnnotatedMeta):
                continue

            if isinstance(meta, ParamMeta):
                if meta.name is not None:
                    name = meta.name
                if meta.doc is not None:
                    summary = meta.doc
                if meta.default != NoDefault:
                    default = meta.default

    return ParamDesc(name, summary, default)


def make_parameter_desc_map(callback: CommandCallable) -> Dict[str, ParamDesc]:
    sig = signature(callback)
    hints = get_type_hints(callback)

    result = dict()
    for param in sig.parameters.values():
        hint = hints.get(param.name, None)
        if (
            hint is not None
            and isinstance(hint, type)
            and issubclass(hint, RUNTIME_REQUEST_TYPES)
        ):
            continue

        desc = make_parameter_desc(param)
        result[desc.key] = desc

    return result


class WorkerCommand:
    def __init__(
        self,
        key: str,
        doc: str,
        params: Dict[str, ParamDesc],
        callback: CommandCallable,
    ):
        self._key = key
        self._doc = doc
        self._params = params
        self._callback = callback
        self._sig = signature(callback)
        self._hints = get_type_hints(callback)

        for param in self._sig.parameters.values():
            if param.kind not in SUPPORTED_PARAMETER_KINDS:
                raise InvalidCommandError(f"Unsupported parameter kind: {param.kind}")

    @property
    def key(self):
        return self._key

    @property
    def doc(self):
        return self._doc

    @property
    def params(self):
        return self._params

    @classmethod
    def from_callback(
        cls,
        callback: CommandCallable,
        *,
        key: Optional[str] = None,
        doc: Optional[str] = None,
        prefix: Optional[str] = DEFAULT_KEY_PREFIX,
    ):
        key = key if key is not None else callback.__name__
        doc = doc if doc is not None else callback.__doc__

        assert key is not None
        if prefix and key.startswith(prefix):
            begin = len(prefix)
            key = key[begin:]

        if not key:
            raise KeyError("key must *NOT* be empty")

        return cls(
            key=key,
            doc=doc if doc is not None else str(),
            params=make_parameter_desc_map(callback),
            callback=callback,
        )

    def as_desc(self):
        return CmdDesc(
            key=self._key,
            doc=self._doc,
            params=list(self._params.values()),
        )

    def bind_kwargs(
        self,
        request: MsgRequest,
        msg_cmd: Optional[MsgCmd] = None,
    ) -> Dict[str, Any]:
        result = dict()

        msg_cmd = msg_cmd if msg_cmd is not None else request.parse_command_argument()
        assert msg_cmd is not None

        for param in self._sig.parameters.values():
            assert param.kind in SUPPORTED_PARAMETER_KINDS
            desc = self._params.get(param.name)
            if desc is not None:
                value = msg_cmd.get(desc.key, desc.default)
            else:
                hint = self._hints.get(param.name, None)
                assert hint is not None
                assert isinstance(hint, type)
                if issubclass(hint, Param):
                    if issubclass(hint, ContentParam):
                        value = ContentParam(msg_cmd.content)
                    elif issubclass(hint, CreatedAtParam):
                        value = CreatedAtParam.from_datetime(request.created_at)
                    elif issubclass(hint, FileParam):
                        if request.files:
                            value = FileParam.from_msg(request.files[0])
                        else:
                            value = None
                    elif issubclass(hint, FilesParam):
                        value = FilesParam.from_msg(request.files)
                    elif issubclass(hint, NicknameParam):
                        value = NicknameParam(request.nickname)
                    elif issubclass(hint, UsernameParam):
                        value = UsernameParam(request.username)
                    elif issubclass(hint, MsgUUIDParam):
                        value = MsgUUIDParam(request.msg_uuid)
                    else:
                        raise CommandRuntimeError(f"Invalid parameter hint: {hint}")
                else:
                    assert issubclass(hint, MsgRequest)
                    value = request

            result[param.name] = value

        return result

    async def __call__(self, request: MsgRequest) -> MsgResponse:
        content: Optional[str] = None
        error: Optional[str] = None
        files = list()
        created_at = tznow()

        try:
            msg_cmd = request.parse_command_argument()
            kwargs = self.bind_kwargs(request, msg_cmd)
            reply = await self._callback(**kwargs)

            if reply is not None:
                if isinstance(reply, ContentReply):
                    content = str(reply)
                elif isinstance(reply, FileReply):
                    files.append(reply.as_msg(created_at))
                elif isinstance(reply, FilesReply):
                    files.extend(reply.as_msg(created_at))
                elif isinstance(reply, ReplyTuple):
                    content = str(reply.content)
                    files.extend(reply.files.as_msg(created_at))
                else:
                    raise CommandRuntimeError(
                        f"Invalid reply type error: {type(reply).__name__}"
                    )
        except BaseException as e:
            logger.exception(e)
            error = str(e)

        return MsgResponse(
            msg_uuid=request.msg_uuid,
            content=content,
            error=error,
            files=files,
            created_at=created_at,
        )
