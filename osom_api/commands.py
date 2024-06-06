# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique
from typing import Final, Sequence

COMMAND_PREFIX: Final[str] = "/"
CONTENT_SEPERATOR: Final[str] = " "
ARGUMENT_SEPERATOR: Final[str] = ","
KV_SEPERATOR: Final[str] = "="

__COMMAND_EXAMPLE__ = "/chat,model=gpt-4o,n=1 your_message"


BASIC_DISCORD_COMMANDS: Final[Sequence[str]] = (
    "ban",
    "gif",
    "kick",
    "me",
    "msg",
    "nick",
    "shrug",
    "spoiler",
    "tableflip",
    "tenor",
    "thread",
    "timeout",
    "tts",
    "unflip",
)


@unique
class EndpointCommands(StrEnum):
    version = auto()
    help = auto()
