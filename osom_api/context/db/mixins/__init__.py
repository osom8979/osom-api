# -*- coding: utf-8 -*-

from osom_api.context.db.mixins.discord_register import DiscordRegister
from osom_api.context.db.mixins.members import Members
from osom_api.context.db.mixins.openai_chat import OpenaiChat
from osom_api.context.db.mixins.progress import Progress
from osom_api.context.db.mixins.telegram_register import TelegramRegister


class DbMixins(
    DiscordRegister,
    Members,
    OpenaiChat,
    Progress,
    TelegramRegister,
):
    pass
