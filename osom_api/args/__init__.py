# -*- coding: utf-8 -*-

from osom_api.args.api import ApiArgs
from osom_api.args.discord import DiscordArgs
from osom_api.args.module import ModuleArgs
from osom_api.args.redis import RedisArgs
from osom_api.args.s3 import S3Args
from osom_api.args.supabase import SupabaseArgs
from osom_api.args.telegram import TelegramArgs

__all__ = [
    "ApiArgs",
    "DiscordArgs",
    "ModuleArgs",
    "RedisArgs",
    "S3Args",
    "SupabaseArgs",
    "TelegramArgs",
]
