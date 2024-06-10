# -*- coding: utf-8 -*-

from dataclasses import dataclass, field
from typing import Any, List


@dataclass
class ParamDesc:
    key: str
    doc: str = ""
    default: Any = None


@dataclass
class CmdDesc:
    key: str
    doc: str = ""
    params: List[ParamDesc] = field(default_factory=lambda: list())
