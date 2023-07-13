# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Callable


def bot_main(args: Namespace, printer: Callable[..., None] = print) -> None:
    assert args is not None
    assert printer is not None
    printer("Not implement error")
