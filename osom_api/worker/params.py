# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List


class Param:
    pass


class ContentParam(str, Param):
    pass


class FileParam(Param):
    name: str
    data: bytes
    mime: str


class FilesParam(List[FileParam], Param):
    pass


class UsernameParam(str, Param):
    pass


class NicknameParam(str, Param):
    pass


class CreatedAtParam(datetime, Param):
    pass


class MsgUUIDParam(str, Param):
    pass
