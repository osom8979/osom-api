# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum, unique
from typing import List, Tuple
from uuid import uuid4


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

    def split_command_argument(self) -> Tuple[str, str]:
        tokens = self.text.split(" ", 1)
        tokens_size = len(tokens)
        assert tokens_size in (1, 2)
        command = tokens[0]
        argument = tokens[1].strip() if tokens_size == 2 else str()
        return command, argument


@dataclass
class MsgResponse:
    msg_uuid: str
    text: str
    files: List[MsgFile] = field(default_factory=list)
