# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any, List


@dataclass
class ParamDesc:
    key: str
    doc: str
    default: Any


@dataclass
class CmdDesc:
    key: str
    doc: str
    params: List[ParamDesc]
