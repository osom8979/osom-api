# -*- coding: utf-8 -*-

from datetime import datetime
from io import StringIO
from typing import Iterable, List, Optional

from type_serialize import decode, encode
from type_serialize.byte.byte_coder import DEFAULT_BYTE_CODING_TYPE
from type_serialize.variables import COMPRESS_LEVEL_TRADEOFF

from osom_api.chrono.datetime import tznow
from osom_api.msg.file import MsgFile, files_repr


class MsgResponse:
    msg_uuid: str
    content: Optional[str]
    error: Optional[str]
    files: List[MsgFile]
    created_at: datetime

    def __init__(
        self,
        msg_uuid: str,
        content: Optional[str] = None,
        error: Optional[str] = None,
        files: Optional[Iterable[MsgFile]] = None,
        created_at: Optional[datetime] = None,
    ):
        self.msg_uuid = msg_uuid
        self.content = content
        self.error = error
        self.files = list(files) if files is not None else list()
        self.created_at = created_at if created_at else tznow()

    def __str__(self):
        return f"{self.__class__.__name__}<{self.msg_uuid}>"

    def __repr__(self):
        buffer = StringIO()
        buffer.write(
            f"{self.__class__.__name__}"
            f"<msg_uuid={self.msg_uuid}"
            f",content={self.content}"
            f",error={self.error}"
            f",files=[{files_repr(self.files)}]"
            f",created_at={self.created_at}>"
        )
        return buffer.getvalue()

    @property
    def has_error(self) -> bool:
        return self.error is not None

    @property
    def reply_content(self) -> str:
        if self.error is not None:
            return self.error
        elif self.content is not None:
            return self.content
        else:
            return str()

    def encode(self, level=COMPRESS_LEVEL_TRADEOFF, coding=DEFAULT_BYTE_CODING_TYPE):
        return encode(self, level=level, coding=coding)

    @classmethod
    def decode(cls, data: bytes, coding=DEFAULT_BYTE_CODING_TYPE):
        result = decode(data, cls=cls, coding=coding)
        assert isinstance(result, cls)
        return result
