# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique


@unique
class MsgProvider(StrEnum):
    anonymous = auto()
    user = auto()
    admin = auto()
    tester = auto()
    master = auto()
    worker = auto()
    discord = auto()
    telegram = auto()
