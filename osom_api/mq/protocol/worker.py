# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class WorkerRequest:
    api: Optional[str] = None
    id: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


@dataclass
class InsertProgressResponse:
    id: str
