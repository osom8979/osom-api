# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.apps.discord.context import DiscordContext


def discord_main(args: Namespace) -> None:
    DiscordContext(args).run()
