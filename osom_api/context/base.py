# -*- coding: utf-8 -*-

from typing import AnyStr, Optional, Sequence

from overrides import override

from osom_api.args import RedisArgs, S3Args, SupabaseArgs
from osom_api.context.db import DbClient
from osom_api.context.mq import MqClient, MqClientCallback
from osom_api.context.s3 import S3Client
from osom_api.msg import MsgProvider


class BaseContextConfig(RedisArgs, S3Args, SupabaseArgs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assert_common_properties()
        self.assert_redis_properties()
        self.assert_s3_properties()
        self.assert_supabase_properties()


class BaseContext(MqClientCallback):
    def __init__(
        self,
        provider: MsgProvider,
        config: BaseContextConfig,
        subscribe_paths: Optional[Sequence[AnyStr]] = None,
    ):
        self._mq = MqClient.from_args(
            args=config,
            mq_callback=self,
            mq_subscribe_paths=subscribe_paths,
        )
        self._db = DbClient.from_args(config)
        self._s3 = S3Client.from_args(config)

        self.provider = provider
        self.command_prefix = config.command_prefix
        self.debug = config.debug
        self.verbose = config.verbose

    async def open_common_context(self) -> None:
        await self._db.open()
        await self._s3.open()
        await self._mq.open()

    async def close_common_context(self) -> None:
        await self._mq.close()
        await self._s3.close()
        await self._db.close()

    @override
    async def on_mq_connect(self) -> None:
        raise NotImplementedError

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        raise NotImplementedError

    @override
    async def on_mq_done(self) -> None:
        raise NotImplementedError

    @property
    def mq(self):
        return self._mq

    @property
    def s3(self):
        return self._s3

    @property
    def db(self):
        return self._db
