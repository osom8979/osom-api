# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique


@unique
class MsgFlow(StrEnum):
    request = auto()
    response = auto()
