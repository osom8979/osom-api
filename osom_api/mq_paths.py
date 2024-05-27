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
REGISTER_PATH: Final[str] = "/osom/api/register"

assert RESPONSE_PATH.startswith(PATH_ROOT)
assert BROADCAST_PATH.startswith(PATH_ROOT)
assert REGISTER_PATH.startswith(PATH_ROOT)

REGISTER_WORKER_PATH: Final[str] = "/osom/api/register/worker"
REGISTER_WORKER_REQUEST_PATH: Final[str] = "/osom/api/register/worker/request"

assert REGISTER_WORKER_PATH.startswith(REGISTER_PATH)
assert REGISTER_WORKER_REQUEST_PATH.startswith(REGISTER_WORKER_PATH)
