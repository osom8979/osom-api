# -*- coding: utf-8 -*-

from functools import reduce
from typing import Final, Optional

from osom_api.arguments import (
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
)

PATH_SEPARATOR: Final[str] = "/"
PATH_ROOT: Final[str] = f"{PATH_SEPARATOR}osom{PATH_SEPARATOR}api"


def redis_address(
    host=DEFAULT_REDIS_HOST,
    port=DEFAULT_REDIS_PORT,
    database=DEFAULT_REDIS_DATABASE,
    password: Optional[str] = None,
    use_tls=False,
) -> str:
    scheme = "rediss" if use_tls else "redis"
    arg_password = f"password={password}&" if password else str()
    return f"{scheme}://{host}:{port}/{database}?{arg_password}"


def join_path(*paths: str, separator=PATH_SEPARATOR, root=PATH_ROOT) -> str:
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
