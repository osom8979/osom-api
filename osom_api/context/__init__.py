# -*- coding: utf-8 -*-

from signal import SIGINT, raise_signal
from typing import Any, Optional

from boto3 import resource as boto3_resource
from openai import AsyncOpenAI
from overrides import override
from supabase import create_client
from supabase._sync.client import SyncClient as SupabaseClient
from supabase.lib.client_options import ClientOptions as SupabaseClientOptions

from osom_api.config import Config
from osom_api.logging.logging import logger
from osom_api.mq.client import MqClient, MqClientCallback


class Context(MqClientCallback):
    _supabase: Optional[SupabaseClient]
    _s3: Any

    def __init__(self, config: Config):
        self._supabase = None
        self._s3 = None

        self._mq = MqClient(
            url=config.redis_url,
            connection_timeout=config.redis_connection_timeout,
            subscribe_timeout=config.redis_subscribe_timeout,
            close_timeout=config.redis_close_timeout,
            callback=self,
            done=None,
            task_name=None,
            debug=config.debug,
            verbose=config.verbose,
        )

        if config.valid_supabase_params:
            assert isinstance(config.supabase_url, str)
            assert isinstance(config.supabase_key, str)
            self._supabase = create_client(
                supabase_url=config.supabase_url,
                supabase_key=config.supabase_key,
                options=SupabaseClientOptions(
                    auto_refresh_token=True,
                    persist_session=True,
                    postgrest_client_timeout=config.supabase_postgrest_timeout,
                    storage_client_timeout=config.supabase_storage_timeout,
                ),
            )

        if config.valid_s3_params:
            assert isinstance(config.s3_endpoint, str)
            assert isinstance(config.s3_access, str)
            assert isinstance(config.s3_secret, str)
            assert isinstance(config.s3_region, str)
            self._s3 = boto3_resource(
                service_name="s3",
                endpoint_url=config.s3_endpoint,
                aws_access_key_id=config.s3_access,
                aws_secret_access_key=config.s3_secret,
                region_name=config.s3_region,
            )

        if config.openai_api_key:
            assert isinstance(config.openai_api_key, str)
            self._openai = AsyncOpenAI(
                api_key=config.openai_api_key,
                timeout=config.openai_timeout,
            )

    @property
    def mq(self) -> MqClient:
        return self._mq

    @property
    def supabase(self) -> SupabaseClient:
        assert self._supabase is not None
        return self._supabase

    @property
    def s3(self) -> Any:
        assert self._s3 is not None
        return self._s3

    @property
    def openai(self) -> AsyncOpenAI:
        assert self._openai is not None
        return self._openai

    async def open_common_context(self) -> None:
        await self._mq.open()

    async def close_common_context(self) -> None:
        await self._mq.close()

    @staticmethod
    def raise_interrupt_signal() -> None:
        raise_signal(SIGINT)

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("The Redis subscription task is completed")
