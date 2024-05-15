# -*- coding: utf-8 -*-

from osom_api.context.db.mixins.discord_register import DiscordRegister
from osom_api.context.db.mixins.file import File
from osom_api.context.db.mixins.members import Members
from osom_api.context.db.mixins.msg import Msg
from osom_api.context.db.mixins.msg2file import Msg2file
from osom_api.context.db.mixins.openai_chat import OpenaiChat
from osom_api.context.db.mixins.progress import Progress
from osom_api.context.db.mixins.reply import Reply
from osom_api.context.db.mixins.telegram_register import TelegramRegister


class DbMixins(
    DiscordRegister,
    File,
    Members,
    Msg,
    Msg2file,
    OpenaiChat,
    Progress,
    Reply,
    TelegramRegister,
):
    pass
