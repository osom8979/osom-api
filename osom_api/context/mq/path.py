# -*- coding: utf-8 -*-

from functools import reduce
from typing import Final, Union

PATH_SEPARATOR: Final[str] = "/"
PATH_ENCODE: Final[str] = "Latin1"

PATH_ROOT: Final[str] = "/osom/api"
QUEUE_PATH: Final[str] = "/osom/api/queue"
QUEUE_DEFAULT_PATH: Final[str] = "/osom/api/queue/default"
RESPONSE_PATH: Final[str] = "/osom/api/response"
BROADCAST_PATH: Final[str] = "/osom/api/broadcast"


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


def make_response_path(request_msg: Union[str, bytes]):
    if isinstance(request_msg, bytes):
        return join_path(RESPONSE_PATH, str(request_msg, encoding=PATH_ENCODE))
    else:
        return join_path(RESPONSE_PATH, request_msg)


def encode_path(path: str) -> bytes:
    return path.encode(PATH_ENCODE)
