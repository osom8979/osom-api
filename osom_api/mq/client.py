# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from asyncio import Event, create_task
from asyncio.exceptions import CancelledError
from typing import Optional, Sequence

from redis.asyncio import from_url
from redis.asyncio.client import PubSub

from osom_api.aio.shield_any import shield_any
from osom_api.arguments import (
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
)
from osom_api.logging.logging import logger
from osom_api.mq.message import Message
from osom_api.mq.utils import redis_address


class MqClientCallback(metaclass=ABCMeta):
    @abstractmethod
    async def on_connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_subscribe(self, channel: bytes, data: bytes) -> None:
        raise NotImplementedError


class MqClient:
    def __init__(
        self,
        host=DEFAULT_REDIS_HOST,
        port=DEFAULT_REDIS_PORT,
        database=DEFAULT_REDIS_DATABASE,
        password: Optional[str] = None,
        use_tls=False,
        ca_cert_path: Optional[str] = None,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        connection_timeout=DEFAULT_REDIS_CONNECTION_TIMEOUT,
        subscribe_timeout=DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
        callback: Optional[MqClientCallback] = None,
        done: Optional[Event] = None,
        task_name: Optional[str] = None,
    ):
        self._redis = from_url(
            redis_address(host, port, database, password, use_tls),
            ssl_keyfile=key_path,
            ssl_certfile=cert_path,
            ssl_ca_certs=ca_cert_path,
            socket_connect_timeout=connection_timeout,
        )
        self._subscribe_timeout = subscribe_timeout
        self._callback = callback
        self._done = done if done is not None else Event()
        self._task = create_task(
            self._redis_main(),
            name=task_name if task_name else self.__class__.__name__,
        )

    @property
    def subscribe_paths(self) -> Sequence[bytes]:
        return tuple()

    def done(self) -> None:
        self._done.set()

    async def _redis_subscribe_main(self, pubsub: PubSub) -> None:
        logger.debug("Requesting a subscription ...")
        await pubsub.subscribe(*self.subscribe_paths)
        logger.info("Subscription completed!")

        while not self._done.is_set():
            msg = await pubsub.get_message(
                ignore_subscribe_messages=True,
                timeout=self._subscribe_timeout,
            )

            if msg is None:
                continue

            msg = Message.from_message(msg)
            if not msg.is_message:
                continue

            channel = msg.channel
            data = msg.data
            logger.debug(f"Data was received on channel {channel} -> {data}")

            if self._callback is not None:
                await shield_any(self._callback.on_subscribe(channel, data), logger)

    async def _redis_main(self) -> None:
        logger.debug("Redis PING ...")
        await self._redis.ping()
        logger.info("Redis PONG!")

        if self._callback is not None:
            await self._callback.on_connect()

        try:
            pubsub = self._redis.pubsub()
            try:
                await self._redis_subscribe_main(pubsub)
            finally:
                await pubsub.close()
        except CancelledError:
            raise
        except BaseException as e:
            logger.error(e)
        finally:
            await self._redis.close()

    async def exists(self, key: str) -> bool:
        exists = 1 == await self._redis.exists(key)
        logger.info(f"Exists '{key}' -> {exists}")
        return exists

    async def get_bytes(self, key: str) -> bytes:
        value = await self._redis.get(key)
        assert isinstance(value, bytes)
        logger.info(f"Get '{key}' -> {value!r}")
        return value

    async def set_bytes(self, key: str, value: bytes) -> None:
        logger.info(f"Set '{key}' -> {value!r}")
        await self._redis.set(key, value)

    async def get_str(self, key: str) -> str:
        return str(await self.get_bytes(key), encoding="utf8")

    async def set_str(self, key: str, value: str) -> None:
        await self.set_bytes(key, value.encode("utf8"))
