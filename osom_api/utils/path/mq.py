# -*- coding: utf-8 -*-

from typing import Final, Union

from osom_api.paths import MQ_REQUEST_PATH, MQ_RESPONSE_PATH
from osom_api.utils.path.join import join_path

PATH_ENCODING: Final[str] = "Latin1"


def make_request_path(worker_name: Union[str, bytes], encoding=PATH_ENCODING) -> str:
    if isinstance(worker_name, bytes):
        return join_path(MQ_REQUEST_PATH, str(worker_name, encoding=encoding))
    else:
        return join_path(MQ_REQUEST_PATH, worker_name)


def make_response_path(msg_uuid: Union[str, bytes], encoding=PATH_ENCODING) -> str:
    if isinstance(msg_uuid, bytes):
        return join_path(MQ_RESPONSE_PATH, str(msg_uuid, encoding=encoding))
    else:
        return join_path(MQ_RESPONSE_PATH, msg_uuid)


def encode_path(path: Union[str, bytes], encoding=PATH_ENCODING) -> bytes:
    if isinstance(path, bytes):
        return path
    else:
        return path.encode(encoding=encoding)
