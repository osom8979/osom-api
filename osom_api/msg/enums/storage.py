# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique


@unique
class MsgStorage(StrEnum):
    s3 = auto()
    r2 = auto()
    supabase = auto()
