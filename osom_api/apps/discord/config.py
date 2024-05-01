# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.config import Config


class DiscordConfig(Config):
    def __init__(
        self,
        discord_application_id: str,
        discord_token: str,
        **kwargs,
    ):
        self.discord_application_id = discord_application_id
        self.discord_token = discord_token
        super().__init__(**kwargs)

    @classmethod
    def from_namespace(cls, args: Namespace):
        if not args.discord_token:
            raise ValueError("A telegram token is required")
        assert isinstance(args.discord_application_id, str)
        assert isinstance(args.discord_token, str)
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))
