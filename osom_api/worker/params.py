# -*- coding: utf-8 -*-

from datetime import datetime
from typing import List, Optional, Sequence

from osom_api.protocols.msg import MsgFile


class Param:
    pass


class BodyParam(str, Param):
    pass


class ContentParam(str, Param):
    pass


class FileParam(Param):
    def __init__(
        self,
        name: Optional[str] = None,
        data: Optional[bytes] = None,
        mime: Optional[str] = None,
    ):
        self.name = name if name else str()
        self.data = data if name else bytes()
        self.mime = mime if name else str()

    @classmethod
    def from_msg(cls, file: MsgFile):
        return cls(file.name, file.content, file.content_type)


class FilesParam(List[FileParam], Param):
    @classmethod
    def from_msg(cls, files: Sequence[MsgFile]):
        result = cls()
        for file in files:
            result.append(FileParam.from_msg(file))
        return result


class UsernameParam(str, Param):
    pass


class NicknameParam(str, Param):
    pass


class CreatedAtParam(datetime, Param):
    @classmethod
    def from_datetime(cls, dt: datetime):
        return cls(
            year=dt.year,
            month=dt.month,
            day=dt.day,
            hour=dt.hour,
            minute=dt.minute,
            second=dt.second,
            microsecond=dt.microsecond,
            tzinfo=dt.tzinfo,
            fold=dt.fold,
        )

    @classmethod
    def now(cls, tz=None):
        return cls.from_datetime(datetime.now(tz=tz))

    @classmethod
    def utcnow(cls):
        return cls.from_datetime(datetime.utcnow())


class MsgUUIDParam(str, Param):
    pass
