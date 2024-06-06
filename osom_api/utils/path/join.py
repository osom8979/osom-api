# -*- coding: utf-8 -*-

from functools import reduce
from typing import Final

PATH_SEPARATOR: Final[str] = "/"


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
