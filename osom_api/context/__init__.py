# -*- coding: utf-8 -*-

from signal import SIGINT, raise_signal
from typing import Optional

from overrides import override

from osom_api.arguments import version as osom_version
from osom_api.config import Config
from osom_api.context.db import DbClient
from osom_api.context.mq import MqClient, MqClientCallback
from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.context.oai import OaiClient
from osom_api.context.s3 import S3Client
from osom_api.logging.logging import logger


class Context(MqClientCallback):
    def __init__(self, config: Config):
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
        self._db = DbClient(
            supabase_url=config.supabase_url,
            supabase_key=config.supabase_key,
            auto_refresh_token=True,
            persist_session=True,
            postgrest_client_timeout=config.supabase_postgrest_timeout,
            storage_client_timeout=config.supabase_storage_timeout,
        )
        self._s3 = S3Client(
            endpoint=config.s3_endpoint,
            access=config.s3_access,
            secret=config.s3_secret,
            region=config.s3_region,
            bucket=config.s3_bucket,
        )
        self._oai = OaiClient(
            api_key=config.openai_api_key,
            timeout=config.openai_timeout,
        )

    @property
    def mq(self):
        return self._mq

    @property
    def db(self):
        return self._db

    @property
    def s3(self):
        return self._s3

    @property
    def oai(self):
        return self._oai

    async def open_common_context(self) -> None:
        await self._mq.open()
        await self._db.open()
        await self._s3.open()
        await self._oai.open()

    async def close_common_context(self) -> None:
        await self._oai.close()
        await self._s3.close()
        await self._db.close()
        await self._mq.close()

    @property
    def version(self):
        return osom_version()

    @property
    def help(self):
        return ""

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

    async def do_message(self, message: MsgRequest) -> Optional[MsgResponse]:
        return None
