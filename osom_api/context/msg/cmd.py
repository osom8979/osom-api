# -*- coding: utf-8 -*-

from typing import Dict, Optional, TypeVar, Union, overload

from osom_api.commands import (
    ARGUMENT_SEPERATOR,
    COMMAND_PREFIX,
    CONTENT_SEPERATOR,
    KV_SEPERATOR,
)
from osom_api.types.string.to_boolean import string_to_boolean

_DefaultT = TypeVar("_DefaultT", str, bool, int, float)


class MsgCmd:
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
