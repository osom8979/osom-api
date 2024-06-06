# -*- coding: utf-8 -*-

from typing import Dict, Optional, TypeVar, Union, overload

from type_serialize import decode, encode
from type_serialize.byte.byte_coder import DEFAULT_BYTE_CODING_TYPE
from type_serialize.variables import COMPRESS_LEVEL_TRADEOFF

from osom_api.commands import (
    ARGUMENT_SEPERATOR,
    COMMAND_PREFIX,
    CONTENT_SEPERATOR,
    KV_SEPERATOR,
)
from osom_api.types.string.to_boolean import string_to_boolean

_DefaultT = TypeVar("_DefaultT", str, bool, int, float)


class MsgCmd:
    command: str
    kwargs: Dict[str, str]
    content: str

    def __init__(
        self,
        command: Optional[str] = None,
        kwargs: Optional[Dict[str, str]] = None,
        content: Optional[str] = None,
    ):
        self.command = command if command else str()
        self.kwargs = kwargs if kwargs else dict()
        self.content = content if content else str()

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

    def __str__(self):
        return f"{self.__class__.__name__}<{self.command}>"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"<command={self.command}"
            f",kwargs={self.kwargs}"
            f",content={self.content}>"
        )

    def encode(self, level=COMPRESS_LEVEL_TRADEOFF, coding=DEFAULT_BYTE_CODING_TYPE):
        return encode(self, level=level, coding=coding)

    @classmethod
    def decode(cls, data: bytes, coding=DEFAULT_BYTE_CODING_TYPE):
        result = decode(data, cls=cls, coding=coding)
        assert isinstance(result, cls)
        return result

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
        default: Optional[_DefaultT] = None,
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
