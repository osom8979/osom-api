# -*- coding: utf-8 -*-

from inspect import iscoroutinefunction
from typing import Awaitable, Callable, Dict, Optional, Union

from overrides import override

from osom_api.args import RedisArgs, S3Args, SupabaseArgs
from osom_api.context.db import DbClient
from osom_api.context.mq import MqClient, MqClientCallback
from osom_api.context.s3 import S3Client
from osom_api.logging.logging import logger
from osom_api.msg import MsgProvider
from osom_api.utils.path.mq import encode_path

SubscriberCallable = Callable[[bytes], Union[None, Awaitable[None]]]


class BaseContextConfig(RedisArgs, S3Args, SupabaseArgs):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.assert_common_properties()
        self.assert_redis_properties()
        self.assert_s3_properties()
        self.assert_supabase_properties()


class BaseContext(MqClientCallback):
    _subscribers: Dict[bytes, SubscriberCallable]

    def __init__(
        self,
        provider: MsgProvider,
        config: BaseContextConfig,
        subscribers: Optional[Dict[Union[str, bytes], SubscriberCallable]] = None,
    ):
        self._subscribers = dict()
        for path, callback in (subscribers if subscribers else dict()).items():
            encoded_path = encode_path(path)
            self._subscribers[encoded_path] = callback

        self._mq = MqClient.from_args(
            args=config,
            mq_callback=self,
            mq_subscribe_paths=list(self._subscribers.keys()),
        )
        self._db = DbClient.from_args(config)
        self._s3 = S3Client.from_args(config)

        self.provider = provider
        self.command_prefix = config.command_prefix
        self.debug = config.debug
        self.verbose = config.verbose

    async def open_base_context(self) -> None:
        await self._db.open()
        await self._s3.open()
        await self._mq.open()

    async def close_base_context(self) -> None:
        await self._mq.close()
        await self._s3.close()
        await self._db.close()

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        coro = self._subscribers.get(channel, None)
        if coro is not None:
            logger.info(f"Recv subscribed message: {channel!r} -> {data!r}")
            if iscoroutinefunction(coro):
                await coro(data)
            else:
                coro(data)
        else:
            logger.warning(f"Couldn't find subscriber for channel: {channel!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    @property
    def mq(self):
        return self._mq

    @property
    def s3(self):
        return self._s3

    @property
    def db(self):
        return self._db
