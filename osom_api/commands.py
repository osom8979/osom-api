# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique
from typing import Final, Sequence

COMMAND_PREFIX: Final[str] = "/"
BODY_SEPERATOR: Final[str] = " "
ARGUMENT_SEPERATOR: Final[str] = ","
KV_SEPERATOR: Final[str] = "="

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
