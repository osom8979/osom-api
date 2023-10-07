# -*- coding: utf-8 -*-

from osom_api.arguments import (
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
)


def redis_address(
    host=DEFAULT_REDIS_HOST,
    port=DEFAULT_REDIS_PORT,
    database=DEFAULT_REDIS_DATABASE,
    use_tls=False,
) -> str:
    scheme = "rediss" if use_tls else "redis"
    return f"{scheme}://{host}:{port}/{database}"
