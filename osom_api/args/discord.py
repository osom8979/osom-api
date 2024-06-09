# -*- coding: utf-8 -*-

from osom_api.args._common import CommonArgs


class DiscordArgs(CommonArgs):
    discord_application_id: str
    discord_token: str

    def assert_discord_properties(self) -> None:
        assert isinstance(self.discord_application_id, str)
        assert isinstance(self.discord_token, str)
