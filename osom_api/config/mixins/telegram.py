# -*- coding: utf-8 -*-


class TelegramProps:
    telegram_token: str

    def assert_telegram_properties(self) -> None:
        assert isinstance(self.telegram_token, str)
