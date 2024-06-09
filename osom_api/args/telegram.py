# -*- coding: utf-8 -*-

from osom_api.args._common import CommonArgs


class TelegramArgs(CommonArgs):
    telegram_token: str

    def assert_telegram_properties(self) -> None:
        assert isinstance(self.telegram_token, str)
