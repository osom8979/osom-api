# -*- coding: utf-8 -*-

from functools import reduce
from typing import Final

PATH_SEPARATOR: Final[str] = "/"
PATH_ENCODE: Final[str] = "Latin1"


def join_path(*paths: str, separator=PATH_SEPARATOR, root=PATH_SEPARATOR) -> str:
    assert paths

    def _join(x: str, y: str) -> str:
        if x[-1] == separator:
            if y[0] == separator:
                return x + y[1:]
            else:
                return x + y
        else:
            if y[0] == separator:
                return x + y
            else:
                return x + separator + y

    return reduce(_join, paths, root)


def encode_path(path: str) -> bytes:
    return path.encode(PATH_ENCODE)


PATH_ROOT: Final[str] = "/osom/api"
QUEUE_PATH: Final[str] = "/osom/api/queue"
QUEUE_COMMON_PATH: Final[str] = "/osom/api/queue/common"
RESPONSE_PATH: Final[str] = "/osom/api/response"
BROADCAST_PATH: Final[str] = "/osom/api/broadcast"
