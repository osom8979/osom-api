# -*- coding: utf-8 -*-

from enum import IntEnum, auto, unique
from dataclasses import dataclass, field
from datetime import datetime
from typing import List


@unique
class MsgProvider(IntEnum):
    Master = auto()
    Worker = auto()
    Discord = auto()
    Telegram = auto()


@dataclass
class File:
    content_type: str
    file_id: str
    file_name: str
    file_size: int
    image_width: int
    image_height: int
    presigned_url: str


@dataclass
class Msg:
    provider: MsgProvider
    message_id: int
    channel_id: int
    username: str
    nickname: str
    text: str
    created_at: datetime
    files: List[File] = field(default_factory=list)
