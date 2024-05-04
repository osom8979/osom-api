# -*- coding: utf-8 -*-

from typing import Optional

from overrides import override

# noinspection PyProtectedMember
from supabase._async.client import AsyncClient, create_client
from supabase.lib.client_options import ClientOptions

from osom_api.arguments import (
    DEFAULT_SUPABASE_POSTGREST_TIMEOUT,
    DEFAULT_SUPABASE_STORAGE_TIMEOUT,
)
from osom_api.db.mixins.discord_register import DiscordRegister
from osom_api.db.mixins.progress import Progress
from osom_api.db.mixins.telegram_register import TelegramRegister
from osom_api.exceptions import InvalidArgumentError, NotInitializedError


class DbClient(DiscordRegister, Progress, TelegramRegister):
    _supabase: Optional[AsyncClient]

    def __init__(
        self,
        supabase_url: Optional[str] = None,
        supabase_key: Optional[str] = None,
        auto_refresh_token=True,
        persist_session=True,
        postgrest_client_timeout=DEFAULT_SUPABASE_POSTGREST_TIMEOUT,
        storage_client_timeout=DEFAULT_SUPABASE_STORAGE_TIMEOUT,
    ):
        self._supabase = None
        self._supabase_url = supabase_url
        self._supabase_key = supabase_key
        self._options = ClientOptions(
            auto_refresh_token=auto_refresh_token,
            persist_session=persist_session,
            postgrest_client_timeout=postgrest_client_timeout,
            storage_client_timeout=storage_client_timeout,
        )

    async def open(self) -> None:
        if not self._supabase_url:
            raise InvalidArgumentError("No supabase url provided")
        if not self._supabase_key:
            raise InvalidArgumentError("No supabase key provided")

        self._supabase = await create_client(
            self._supabase_url,
            self._supabase_key,
            self._options,
        )

    async def close(self) -> None:
        self._supabase = None

    @property
    @override
    def supabase(self) -> AsyncClient:
        if self._supabase is None:
            raise NotInitializedError("Client is not initialized")
        return self._supabase
