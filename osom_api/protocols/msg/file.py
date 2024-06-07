# -*- coding: utf-8 -*-

from datetime import datetime
from io import StringIO
from typing import List, Optional
from uuid import uuid4

from osom_api.chrono.datetime import tznow
from osom_api.protocols.msg.enums.provider import MsgProvider


class MsgFile:
    def __init__(
        self,
        provider: MsgProvider,
        native_id: str,
        name: str,
        content: Optional[bytes] = None,
        content_type: Optional[str] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        created_at: Optional[datetime] = None,
        file_uuid: Optional[str] = None,
    ):
        self.provider = provider
        self.native_id = native_id
        self.name = name
        self.content = content
        self.content_type = content_type
        self.width = width
        self.height = height
        self.created_at = created_at if created_at else tznow()
        self.file_uuid = file_uuid if file_uuid else str(uuid4())

    @property
    def has_content(self) -> bool:
        return self.content is not None

    @property
    def content_size(self) -> int:
        return len(self.content) if self.content is not None else 0

    @property
    def path(self):
        return f"/msg/{self.provider.name}/{self.file_uuid}"

    def __str__(self):
        return f"{self.__class__.__name__}<{self.name}>"

    def __repr__(self):
        return (
            f"{self.__class__.__name__}"
            f"<provider={self.provider.name}"
            f",file_id={self.native_id}"
            f",file_name={self.name}"
            f",content_size={self.content_size}"
            f",content_type={self.content_type}"
            f",image={self.width}x{self.height}"
            f",created_at={self.created_at}"
            f",file_uuid={self.file_uuid}>"
        )


def files_repr(files: List[MsgFile]) -> str:
    buffer = StringIO()
    if len(files) >= 1:
        f = files[0]
        buffer.write(f"{f.name}({f.file_uuid})")
    for f in files[1:]:
        buffer.write(f",{f.name}({f.file_uuid})")
    return buffer.getvalue()
