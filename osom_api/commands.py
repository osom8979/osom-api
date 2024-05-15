# -*- coding: utf-8 -*-

from typing import Final, Sequence

COMMAND_PREFIX: Final[str] = "/"
CONTENT_SEPERATOR: Final[str] = " "
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
