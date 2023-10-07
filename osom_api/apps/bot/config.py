# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.common.config import CommonConfig


class BotConfig(CommonConfig):
    def __init__(
        self,
        telegram_token: str,
        **kwargs,
    ):
        self.telegram_token = telegram_token
        super().__init__(**kwargs)

    @classmethod
    def from_namespace(cls, args: Namespace):
        if not args.telegram_token:
            raise ValueError("A telegram token is required")
        assert isinstance(args.telegram_token, str)
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))
