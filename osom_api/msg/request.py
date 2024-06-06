# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Iterable, List, Optional
from uuid import uuid4

from type_serialize import decode, encode
from type_serialize.byte.byte_coder import DEFAULT_BYTE_CODING_TYPE
from type_serialize.variables import COMPRESS_LEVEL_TRADEOFF

from osom_api.chrono.datetime import tznow
from osom_api.commands import (
    ARGUMENT_SEPERATOR,
    COMMAND_PREFIX,
    CONTENT_SEPERATOR,
    KV_SEPERATOR,
)
from osom_api.exceptions import InvalidCommandError
from osom_api.msg.cmd import MsgCmd
from osom_api.msg.enums.provider import MsgProvider
from osom_api.msg.file import MsgFile, files_repr


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
    msg_cmd: Optional[MsgCmd]

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
        *,
        command_prefix=COMMAND_PREFIX,
        content_seperator=CONTENT_SEPERATOR,
        argument_seperator=ARGUMENT_SEPERATOR,
        kv_seperator=KV_SEPERATOR,
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

        if self.content and self.content.startswith(command_prefix):
            self.msg_cmd = MsgCmd.from_text(
                text=self.content,
                command_prefix=command_prefix,
                content_seperator=content_seperator,
                argument_seperator=argument_seperator,
                kv_seperator=kv_seperator,
            )
        else:
            self.msg_cmd = None

    def __str__(self):
        return f"{self.__class__.__name__}<{self.msg_uuid}>"

    def __repr__(self):
        return (
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
            f",msg_cmd={bool(self.msg_cmd is not None)}>"
        )

    def encode(self, level=COMPRESS_LEVEL_TRADEOFF, coding=DEFAULT_BYTE_CODING_TYPE):
        return encode(self, level=level, coding=coding)

    @classmethod
    def decode(cls, data: bytes, coding=DEFAULT_BYTE_CODING_TYPE):
        result = decode(data, cls=cls, coding=coding)
        assert isinstance(result, cls)
        return result

    def is_command(self) -> bool:
        return True if self.msg_cmd is not None else False

    def get_command(self) -> str:
        if self.msg_cmd is None:
            raise InvalidCommandError("This message is not a command")
        return self.msg_cmd.command

    def get_command_kwargs(self):
        if self.msg_cmd is None:
            raise InvalidCommandError("This message is not a command")
        return self.msg_cmd.kwargs

    def get_command_content(self):
        if self.msg_cmd is None:
            raise InvalidCommandError("This message is not a command")
        return self.msg_cmd.content
