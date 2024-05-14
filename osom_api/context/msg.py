# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, unique
from io import StringIO
from typing import Dict, List, Optional, TypeVar, Union, overload
from uuid import uuid4

from osom_api.commands import COMMAND_PREFIX
from osom_api.types.string.to_boolean import string_to_boolean

DefaultT = TypeVar("DefaultT", str, bool, int, float)


@unique
class MsgProvider(IntEnum):
    Master = 0
    Worker = 1
    Discord = 2
    Telegram = 3


@dataclass
class MsgFile:
    content_type: str
    file_id: str
    file_name: str
    file_size: int
    image_width: int
    image_height: int
    content: bytes
    file_uuid: str = field(default_factory=lambda: uuid4().hex)


@dataclass
class MsgCommandArgument:
    command: str
    kwargs: Dict[str, str] = field(default_factory=dict)
    content: Optional[str] = None

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


@dataclass
class MsgRequest:
    provider: MsgProvider
    message_id: int
    channel_id: int
    username: str
    nickname: str
    text: str
    created_at: datetime
    files: List[MsgFile] = field(default_factory=list)
    msg_uuid: str = field(default_factory=lambda: uuid4().hex)

    def __repr__(self):
        buffer = StringIO()
        buffer.write(self.__class__.__name__)
        buffer.write(f"<provider={self.provider.name}")
        buffer.write(f",message_id={self.message_id}")
        buffer.write(f",channel_id={self.channel_id}")
        buffer.write(f",username={self.username}")
        buffer.write(f",nickname={self.nickname}")
        buffer.write(f",text={self.text}")
        buffer.write(f",created_at={self.created_at}")
        buffer.write(",files=[")
        if len(self.files) >= 1:
            f = self.files[0]
            buffer.write(f"{f.file_name}({f.file_uuid})")
        for f in self.files[1:]:
            buffer.write(f",{f.file_name}({f.file_uuid})")
        buffer.write(f"],msg_uuid={self.msg_uuid}>")
        return buffer.getvalue()

    def is_command(self):
        return self.text.startswith(COMMAND_PREFIX)

    def parse_command_argument(self):
        tokens = self.text.split(" ", 1)
        assert len(tokens) in (1, 2)
        command_arguments = tokens[0].split(",")

        command = command_arguments[0]
        assert command.startswith(COMMAND_PREFIX)
        command_begin = len(COMMAND_PREFIX)
        command = command[command_begin:]

        kwargs = dict()
        for arg in command_arguments[1:]:
            if arg.find("=") == -1:
                kwargs[arg] = str()
            else:
                key, value = arg.split("=", 1)
                kwargs[key] = value

        content = tokens[1].strip() if len(tokens) == 2 else str()

        return MsgCommandArgument(command, kwargs, content)

    @property
    def command(self):
        return self.parse_command_argument().command


@dataclass
class MsgResponse:
    msg_uuid: str
    text: Optional[str] = None
    files: List[MsgFile] = field(default_factory=list)

    @property
    def reply_content(self) -> str:
        return self.text if self.text else ""


class MsgResponseError(Exception):
    msg_uuid: str

    def __init__(self, msg_uuid: str, message: Optional[str] = None):
        super().__init__(message)
        self.msg_uuid = msg_uuid
