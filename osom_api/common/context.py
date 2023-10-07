# -*- coding: utf-8 -*-

from signal import SIGINT, raise_signal

from boto3 import resource as boto3_resource
from overrides import override
from supabase import create_client
from supabase.client import ClientOptions as SupabaseClientOptions

from osom_api.common.config import CommonConfig
from osom_api.logging.logging import logger
from osom_api.mq.client import MqClient, MqClientCallback


class CommonContext(MqClientCallback):
    def __init__(self, config: CommonConfig):
        self._mq = MqClient(
            host=config.redis_host,
            port=config.redis_port,
            database=config.redis_database,
            password=config.redis_password,
            use_tls=config.redis_use_tls,
            ca_cert_path=config.redis_ca_cert,
            cert_path=config.redis_cert,
            key_path=config.redis_key,
            connection_timeout=config.redis_connection_timeout,
            subscribe_timeout=config.redis_subscribe_timeout,
            close_timeout=config.redis_close_timeout,
            callback=self,
            done=None,
            task_name=None,
            debug=config.debug,
            verbose=config.verbose,
        )

        if not config.supabase_url:
            raise ValueError("A supabase url is required")
        if not config.supabase_key:
            raise ValueError("A supabase key is required")

        self._supabase = create_client(
            supabase_url=config.supabase_url,
            supabase_key=config.supabase_key,
            options=SupabaseClientOptions(
                auto_refresh_token=True,
                persist_session=True,
            ),
        )

        if not config.s3_endpoint:
            raise ValueError("A s3 endpoint is required")
        if not config.s3_access:
            raise ValueError("A s3 access is required")
        if not config.s3_secret:
            raise ValueError("A s3 secret is required")
        if not config.s3_region:
            raise ValueError("A s3 region is required")

        self._s3 = boto3_resource(
            service_name="s3",
            endpoint_url=config.s3_endpoint,
            aws_access_key_id=config.s3_access,
            aws_secret_access_key=config.s3_secret,
            region_name=config.s3_region,
        )

    @property
    def mq(self):
        return self._mq

    @property
    def supabase(self):
        return self._supabase

    @property
    def s3(self):
        return self._s3

    async def common_open(self) -> None:
        await self._mq.open()

    async def common_close(self) -> None:
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
        logger.info("The Redis subscription task is completed")
