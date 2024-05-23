# -*- coding: utf-8 -*-

from typing import Any, NamedTuple, Sequence


class ParamDesc(NamedTuple):
    key: str
    doc: str
    default: Any


class CmdDesc(NamedTuple):
    key: str
    doc: str
    params: Sequence[ParamDesc]
