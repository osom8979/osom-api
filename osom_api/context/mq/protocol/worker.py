# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Final, Optional

WORKER_REQUEST_API_KEY: Final[str] = "api"
WORKER_REQUEST_MSG_KEY: Final[str] = "msg"
WORKER_REQUEST_DATA_KEY: Final[str] = "data"


@dataclass
class CreateProgressResponse:
    id: str
    """UUID of generated Progress."""


@dataclass
class UpdateProgressRequest:
    id: str
    """UUID of progress."""

    value: Optional[str] = None
    """The value of the progress."""
