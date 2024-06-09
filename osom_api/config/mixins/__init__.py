# -*- coding: utf-8 -*-

from osom_api.config.mixins.api import ApiProps
from osom_api.config.mixins.common import CommonProps
from osom_api.config.mixins.discord import DiscordProps
from osom_api.config.mixins.module import ModuleProps
from osom_api.config.mixins.redis import RedisProps
from osom_api.config.mixins.s3 import S3Props
from osom_api.config.mixins.supabase import SupabaseProps
from osom_api.config.mixins.telegram import TelegramProps

__all__ = [
    "ApiProps",
    "CommonProps",
    "DiscordProps",
    "ModuleProps",
    "RedisProps",
    "S3Props",
    "SupabaseProps",
    "TelegramProps",
]
