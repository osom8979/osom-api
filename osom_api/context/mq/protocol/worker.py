# -*- coding: utf-8 -*-

from dataclasses import dataclass
from enum import StrEnum, auto, unique
from typing import Final, Optional


@unique
class Keys(StrEnum):
    id = auto()
    cmd = auto()
    data = auto()


WORKER_REQUEST_ID_KEY: Final[str] = Keys.id
WORKER_REQUEST_CMD_KEY: Final[str] = Keys.cmd
WORKER_REQUEST_DATA_KEY: Final[str] = Keys.data


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
