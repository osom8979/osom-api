# -*- coding: utf-8 -*-

from datetime import datetime
from enum import IntEnum, unique
from io import StringIO
from typing import Dict, Final, Iterable, List, Optional, TypeVar, Union, overload
from uuid import uuid4

from osom_api.commands import (
    ARGUMENT_SEPERATOR,
    COMMAND_PREFIX,
    CONTENT_SEPERATOR,
    KV_SEPERATOR,
)
from osom_api.exceptions import InvalidCommandError
from osom_api.types.string.to_boolean import string_to_boolean

DefaultT = TypeVar("DefaultT", str, bool, int, float)

DEFAULT_CONTENT_TYPE: Final[str] = "application/octet-stream"


@unique
class MsgProvider(IntEnum):
    Master = 0
    Worker = 1
    Discord = 2
    Telegram = 3


class MsgFile:
    def __init__(
        self,
        provider: MsgProvider,
        file_id: str,
        file_name: str,
        content: bytes,
        content_type: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        created_at: Optional[datetime] = None,
        file_uuid: Optional[str] = None,
    ):
        self.provider = provider
        self.file_id = file_id
        self.file_name = file_name
        self.content = content
        self.content_type = content_type if content_type else DEFAULT_CONTENT_TYPE
        self.width = width if width is not None else 0
        self.height = height if height is not None else 0
        self.created_at = created_at if created_at else datetime.utcnow()
        self.file_uuid = file_uuid if file_uuid else uuid4().hex

    @property
    def content_size(self) -> int:
        return len(self.content)

    def __str__(self):
        return f"{self.__class__.__name__}<{self.file_name}>"

    def __repr__(self):
        buffer = StringIO()
        buffer.write(
            f"{self.__class__.__name__}"
            f"<provider={self.provider.name}"
            f",file_id={self.file_id}"
            f",file_name={self.file_name}"
            f",content_size={self.content_size}"
            f",content_type={self.content_type}"
            f",image={self.width}x{self.height}"
            f",created_at={self.created_at}"
            f",file_uuid={self.file_uuid}>"
        )
        return buffer.getvalue()


def files_repr(files: List[MsgFile]) -> str:
    buffer = StringIO()
    if len(files) >= 1:
        f = files[0]
        buffer.write(f"{f.file_name}({f.file_uuid})")
    for f in files[1:]:
        buffer.write(f",{f.file_name}({f.file_uuid})")
    return buffer.getvalue()


class MsgCommandArgument:
    def __init__(
        self,
        command: str,
        kwargs: Dict[str, str],
        content: str,
    ):
        self.command = command
        self.kwargs = kwargs
        self.content = content

    @classmethod
    def from_text(
        cls,
        text: str,
        command_prefix=COMMAND_PREFIX,
        content_seperator=CONTENT_SEPERATOR,
        argument_seperator=ARGUMENT_SEPERATOR,
        kv_seperator=KV_SEPERATOR,
    ):
        tokens = text.split(content_seperator, 1)
        assert len(tokens) in (1, 2)
        command_arguments = tokens[0].split(argument_seperator)

        command = command_arguments[0]
        assert command.startswith(command_prefix)
        command_begin = len(command_prefix)
        command = command[command_begin:]

        kwargs = dict()
        for arg in command_arguments[1:]:
            kv = arg.split(kv_seperator, 1)
            key = kv[0]
            if len(kv) == 1:
                kwargs[key] = str()
            else:
                assert len(kv) == 2
                kwargs[key] = kv[1]

        content = tokens[1].strip() if len(tokens) == 2 else str()
        return cls(command, kwargs, content)

    # fmt: off
    @overload
    def get(self, key: str) -> Optional[str]: ...
    @overload
    def get(self, key: str, default: str) -> str: ...
    @overload
    def get(self, key: str, default: bool) -> bool: ...
    @overload
    def get(self, key: str, default: int) -> int: ...
    @overload
    def get(self, key: str, default: float) -> float: ...
    # fmt: on

    def get(
        self,
        key: str,
        default: Optional[DefaultT] = None,
    ) -> Optional[Union[str, bool, int, float]]:
        if default is None:
            return self.kwargs.get(key)
        value = self.kwargs.get(key, str(default))
        if isinstance(default, str):
            return value
        elif isinstance(default, bool):
            return string_to_boolean(value)
        elif isinstance(default, int):
            return int(value)
        elif isinstance(default, float):
            return float(value)
        else:
            raise TypeError(f"Unsupported default type: {type(default).__name__}")


class MsgRequest:
    def __init__(
        self,
        provider: MsgProvider,
        message_id: int,
        channel_id: int,
        content: Optional[str] = None,
        username: Optional[str] = None,
        nickname: Optional[str] = None,
        files: Optional[Iterable[MsgFile]] = None,
        created_at: Optional[datetime] = None,
        msg_uuid: Optional[str] = None,
    ):
        self.provider = provider
        self.message_id = message_id
        self.channel_id = channel_id
        self.content = content if content else str()
        self.username = username if username else str()
        self.nickname = nickname if nickname else str()
        self.files = list(files) if files is not None else list()
        self.created_at = created_at if created_at else datetime.utcnow()
        self.msg_uuid = msg_uuid if msg_uuid else uuid4().hex

    def __str__(self):
        return f"{self.__class__.__name__}<{self.msg_uuid}>"

    def __repr__(self):
        buffer = StringIO()
        buffer.write(
            f"{self.__class__.__name__}"
            f"<provider={self.provider.name}"
            f",message_id={self.message_id}"
            f",channel_id={self.channel_id}"
            f",username={self.username}"
            f",nickname={self.nickname}"
            f",content={self.content}"
            f",files=[{files_repr(self.files)}]"
            f",created_at={self.created_at}"
            f",msg_uuid={self.msg_uuid}>"
        )
        return buffer.getvalue()

    def is_command(self):
        return self.content.startswith(COMMAND_PREFIX)

    def parse_command_argument(self):
        if not self.is_command():
            raise InvalidCommandError
        return MsgCommandArgument.from_text(self.content, COMMAND_PREFIX)

    @property
    def command(self):
        return self.parse_command_argument().command


class MsgResponse:
    def __init__(
        self,
        msg_uuid: str,
        content: Optional[str] = None,
        files: Optional[Iterable[MsgFile]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.msg_uuid = msg_uuid
        self.content = content if content else str()
        self.files = list(files) if files is not None else list()
        self.created_at = created_at if created_at else datetime.utcnow()

    def __str__(self):
        return f"{self.__class__.__name__}<{self.msg_uuid}>"

    def __repr__(self):
        buffer = StringIO()
        buffer.write(
            f"{self.__class__.__name__}"
            f"<msg_uuid={self.msg_uuid}"
            f",content={self.content}"
            f",files=[{files_repr(self.files)}]"
            f",created_at={self.created_at}>"
        )
        return buffer.getvalue()

    @property
    def reply_content(self) -> str:
        return self.content if self.content else ""


class MsgError(Exception):
    msg_uuid: str

    def __init__(self, msg_uuid: str, message: Optional[str] = None):
        super().__init__(message)
        self.msg_uuid = msg_uuid
