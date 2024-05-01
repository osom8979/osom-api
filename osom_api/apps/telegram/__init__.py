# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.apps.telegram.context import TelegramContext


def telegram_main(args: Namespace) -> None:
    TelegramContext(args).run()
