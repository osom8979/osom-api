# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class WorkerRequest:
    api: Optional[str] = None
    id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class CreateProgressData:
    uuid: str


@dataclass
class CreateProgressResponse:
    error: Optional[str] = None
    data: Optional[CreateProgressData] = None
