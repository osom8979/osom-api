# -*- coding: utf-8 -*-

from typing import Final

PATH_SEPARATOR: Final[str] = "/"
PATH_ENCODE: Final[str] = "Latin1"

PATH_ROOT: Final[str] = "/osom/api"

assert PATH_ROOT.startswith(PATH_SEPARATOR)

QUEUE_PATH: Final[str] = "/osom/api/queue"
QUEUE_DEFAULT_PATH: Final[str] = "/osom/api/queue/default"

assert QUEUE_PATH.startswith(PATH_ROOT)
assert QUEUE_DEFAULT_PATH.startswith(QUEUE_PATH)

RESPONSE_PATH: Final[str] = "/osom/api/response"
BROADCAST_PATH: Final[str] = "/osom/api/broadcast"

assert RESPONSE_PATH.startswith(PATH_ROOT)
assert BROADCAST_PATH.startswith(PATH_ROOT)
