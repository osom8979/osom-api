# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.config.base import BaseConfig
from osom_api.config.mixins import CommonProps, DiscordProps, RedisProps


class DiscordConfig(BaseConfig, CommonProps, DiscordProps, RedisProps):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_common_properties()
        self.assert_discord_properties()
        self.assert_redis_properties()
