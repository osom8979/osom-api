# -*- coding: utf-8 -*-

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Union
from uuid import uuid4

from osom_api.chrono.datetime import tznow
from osom_api.protocols.msg import MsgFile, MsgProvider

ContentReply = str


@dataclass
class FileReply:
    name: str
    data: bytes
    mime: Optional[str] = None

    def as_msg(self, created_at: Optional[datetime] = None):
        file_uuid = str(uuid4())
        return MsgFile(
            provider=MsgProvider.worker,
            native_id=file_uuid,
            name=self.name,
            content=self.data,
            content_type=self.mime,
            created_at=created_at if created_at is not None else tznow(),
            file_uuid=file_uuid,
        )


class FilesReply(List[FileReply]):
    def as_msg(self, created_at: Optional[datetime] = None):
        return [file.as_msg(created_at) for file in self]


@dataclass
class ReplyTuple:
    content: ContentReply
    files: FilesReply


Reply = Union[
    None,
    ContentReply,
    FileReply,
    FilesReply,
    ReplyTuple,
]
