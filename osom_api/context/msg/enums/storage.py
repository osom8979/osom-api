# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique


@unique
class MsgFileStorage(StrEnum):
    s3 = auto()
    r2 = auto()
    supabase = auto()
