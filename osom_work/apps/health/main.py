# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Callable
from urllib.request import urlopen


def health_main(args: Namespace, printer: Callable[..., None] = print) -> None:
    assert args is not None
    assert printer is not None

    secure = args.secure
    host = args.host
    port = args.port
    timeout = args.timeout
    path = args.path

    assert isinstance(secure, bool)
    assert isinstance(host, str)
    assert isinstance(port, int)
    assert isinstance(timeout, float)
    assert isinstance(path, str)

    scheme = "https" if secure else "http"
    abs_path = path if path[0] == "/" else f"/{path}"
    url = f"{scheme}://{host}:{port}{abs_path}"

    result = urlopen(url, timeout=timeout)
    assert isinstance(result.status, int)

    if result.status != 200:
        raise ValueError(f"Heartbreak status: {result.status}")
