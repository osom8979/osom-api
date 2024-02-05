# -*- coding: utf-8 -*-

from functools import reduce
from typing import Final

PATH_SEPARATOR: Final[str] = "/"
PATH_ENCODE: Final[str] = "Latin1"
PATH_ROOT: Final[str] = f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api"
assert PATH_ROOT == "/osom/api"


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


BROADCAST_PATH: Final[str] = join_path(PATH_ROOT, "broadcast")
BROADCAST_BYTES: Final[bytes] = BROADCAST_PATH.encode(PATH_ENCODE)

QUEUE_PATH: Final[str] = join_path(PATH_ROOT, "queue")
QUEUE_BYTES: Final[bytes] = QUEUE_PATH.encode(PATH_ENCODE)
