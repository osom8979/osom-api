# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.args import DiscordArgs
from osom_api.context.base import BaseContextConfig


class DiscordConfig(BaseContextConfig, DiscordArgs):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_discord_properties()
