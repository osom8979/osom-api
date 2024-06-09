# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.args import TelegramArgs
from osom_api.context.base import BaseContextConfig


class TelegramConfig(BaseContextConfig, TelegramArgs):
    def __init__(self, args: Namespace):
        super().__init__(**self.namespace_to_dict(args))
        self.assert_common_properties()
        self.assert_redis_properties()
        self.assert_telegram_properties()
