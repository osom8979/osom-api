# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import StrEnum, unique
from typing import Final, Optional

WORKER_REQUEST_API_KEY: Final[str] = "api"
WORKER_REQUEST_MSG_KEY: Final[str] = "msg"
WORKER_REQUEST_DATA_KEY: Final[str] = "data"


@unique
class Keys(StrEnum):
    api = WORKER_REQUEST_API_KEY
    msg = WORKER_REQUEST_MSG_KEY
    data = WORKER_REQUEST_DATA_KEY


assert Keys.api == WORKER_REQUEST_API_KEY
assert Keys.msg == WORKER_REQUEST_MSG_KEY
assert Keys.data == WORKER_REQUEST_DATA_KEY


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
