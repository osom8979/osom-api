# -*- coding: utf-8 -*-

from typing import List, NamedTuple, Optional, Union


class FileReply:
    name: str
    data: bytes
    mime: Optional[str] = None


class FilesReply(List[FileReply]):
    pass


class ReplyTuple(NamedTuple):
    content: str
    files: FilesReply


Reply = Union[
    None,
    str,
    FileReply,
    FilesReply,
    ReplyTuple,
]
