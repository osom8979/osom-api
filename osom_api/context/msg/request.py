# -*- coding: utf-8 -*-

from datetime import datetime
from io import StringIO
from typing import Iterable, List, Optional
from uuid import uuid4

from type_serialize import decode, encode
from type_serialize.byte.byte_coder import DEFAULT_BYTE_CODING_TYPE
from type_serialize.variables import COMPRESS_LEVEL_TRADEOFF

from osom_api.chrono.datetime import tznow
from osom_api.commands import COMMAND_PREFIX
from osom_api.context.msg.cmd import MsgCmd
from osom_api.context.msg.enums.provider import MsgProvider
from osom_api.context.msg.file import MsgFile, files_repr
from osom_api.exceptions import InvalidCommandError


class MsgRequest:
    provider: MsgProvider
    message_id: Optional[int]
    channel_id: Optional[int]
    content: Optional[str]
    username: Optional[str]
    nickname: Optional[str]
    files: List[MsgFile]
    created_at: datetime
    msg_uuid: str

    def __init__(
        self,
        provider: MsgProvider,
        message_id: Optional[int] = None,
        channel_id: Optional[int] = None,
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
        self.content = content
        self.username = username
        self.nickname = nickname
        self.files = list(files) if files is not None else list()
        self.created_at = created_at if created_at else tznow()
        self.msg_uuid = msg_uuid if msg_uuid else str(uuid4())

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
        return MsgCmd.from_text(self.content, COMMAND_PREFIX)

    def get_command(self):
        return self.parse_command_argument().command

    def encode(self, level=COMPRESS_LEVEL_TRADEOFF, coding=DEFAULT_BYTE_CODING_TYPE):
        return encode(self, level=level, coding=coding)

    @classmethod
    def decode(cls, data: bytes, coding=DEFAULT_BYTE_CODING_TYPE):
        result = decode(data, cls=cls, coding=coding)
        assert isinstance(result, cls)
        return result
