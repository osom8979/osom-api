# -*- coding: utf-8 -*-

from argparse import Namespace
from urllib.request import urlopen


def health_main(args: Namespace) -> None:
    assert isinstance(args.uri, str)
    assert isinstance(args.timeout, float)

    result = urlopen(args.uri, timeout=args.timeout)
    assert isinstance(result.status, int)

    if result.status != 200:
        raise ValueError(f"Heartbreak status: {result.status}")
