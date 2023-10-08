# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.apps.bot.context import BotContext


def bot_main(args: Namespace) -> None:
    BotContext(args).run()
