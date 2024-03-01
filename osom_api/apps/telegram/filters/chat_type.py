# -*- coding: utf-8 -*-

from aiogram.filters import Filter
from aiogram.types import Message


class ChatTypeFilter(Filter):
    def __init__(self, private=False, group=False, supergroup=False, channel=False):
        self.chat_types = set()
        if private:
            self.chat_types.add("private")
        if group:
            self.chat_types.add("group")
        if supergroup:
            self.chat_types.add("supergroup")
        if channel:
            self.chat_types.add("channel")

    async def __call__(self, message: Message) -> bool:
        return message.chat.type in self.chat_types
