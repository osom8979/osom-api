# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class WorkerRequest:
    api: str
    id: str
    data: Any


@dataclass
class CreateProgressData:
    uuid: str


@dataclass
class CreateProgressResponse:
    error: Optional[str]
    data: Optional[CreateProgressData]
