# -*- coding: utf-8 -*-

from typing import Final, Union

from osom_api.paths import MQ_RESPONSE_PATH
from osom_api.utils.path.join import join_path

PATH_ENCODE: Final[str] = "Latin1"


def make_response_path(request_msg: Union[str, bytes]):
    if isinstance(request_msg, bytes):
        return join_path(MQ_RESPONSE_PATH, str(request_msg, encoding=PATH_ENCODE))
    else:
        return join_path(MQ_RESPONSE_PATH, request_msg)


def encode_path(path: str) -> bytes:
    return path.encode(PATH_ENCODE)
