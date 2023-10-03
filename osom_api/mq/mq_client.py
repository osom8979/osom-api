# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from asyncio import Event, Task, create_task
from asyncio import sleep as asyncio_sleep
from asyncio.exceptions import CancelledError
from io import StringIO
from typing import Final, Optional, Sequence

from redis.asyncio import Redis, from_url
from redis.asyncio.client import PubSub

from osom_api.aio.shield_any import shield_any
from osom_api.arguments import (
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_DATABASE,
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_RECONNECT_DELAY,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
)
from osom_api.logging.logging import logger
from osom_api.mq.message import Message

DEFAULT_TASK_NAME: Final[str] = "MqTask"


class MqAlreadyOpenError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class MqNotOpenError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class MqRedisIsNoneError(RuntimeError):
    def __init__(self, *args):
        super().__init__(*args)


class MqClientCallback(metaclass=ABCMeta):
    @abstractmethod
    async def on_connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_subscribe(self, channel: bytes, data: bytes) -> None:
        raise NotImplementedError


class MqClient:
    _task: Optional[Task[None]]
    _redis: Optional[Redis]

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
        reconnect_delay=DEFAULT_REDIS_RECONNECT_DELAY,
        callback: Optional[MqClientCallback] = None,
        task_name=DEFAULT_TASK_NAME,
    ):
        self._host = host
        self._port = port
        self._database = database
        self._password = password
        self._use_tls = use_tls
        self._ca_cert_path = ca_cert_path
        self._cert_path = cert_path
        self._key_path = key_path
        self._conn_timeout = connection_timeout
        self._subscribe_timeout = subscribe_timeout
        self._reconnect_delay = reconnect_delay
        self._callback = callback
        self._task_name = task_name

        self._redis = None
        self._task = None
        self._done = Event()

    @property
    def scheme(self) -> str:
        return "rediss" if self._use_tls else "redis"

    @property
    def url(self) -> str:
        buffer = StringIO()
        buffer.write(f"{self.scheme}://{self._host}:{self._port}/{self._database}?")
        if self._password:
            buffer.write(f"password={self._password}&")
        return buffer.getvalue()

    @property
    def subscribe_paths(self) -> Sequence[bytes]:
        return tuple()

    def done(self) -> None:
        self._done.set()

    async def open(self) -> None:
        if self._task is not None:
            raise MqAlreadyOpenError("The Redis task is already open")

        self._done.clear()
        self._task = create_task(self._main(), name=self._task_name)

    async def close(self) -> None:
        if self._task is None:
            raise MqNotOpenError("Redis task does not open")

        self._done.set()

        assert self._task is not None
        self._task.cancel("The task has been cancelled")
        try:
            await self._task
        except CancelledError as e:
            logger.debug(e)
        self._task = None

    async def __aenter__(self):
        await self.open()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def _subscribe_iter(self, pubsub: PubSub) -> None:
        logger.debug(f"Requesting a subscription: {self.subscribe_paths}")
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

            if self._callback is None:
                continue

            await shield_any(self._callback.on_subscribe(channel, data), logger)

    async def _conn_iter(self, redis: Redis) -> None:
        logger.debug("Redis ping ...")
        await redis.ping()
        logger.debug("Redis pong!")

        if self._callback is not None:
            await self._callback.on_connect()

        while not self._done.is_set():
            pubsub = redis.pubsub()
            try:
                await self._subscribe_iter(pubsub)
            finally:
                await pubsub.close()

    def create_redis_instance(self) -> Redis:
        logger.debug(f"Create redis instance: '{self.url}'")
        return from_url(
            self.url,
            ssl_keyfile=self._key_path,
            ssl_certfile=self._cert_path,
            ssl_ca_certs=self._ca_cert_path,
        )

    async def _main(self) -> None:
        while not self._done.is_set():
            self._redis = self.create_redis_instance()

            try:
                assert self._redis is not None
                await self._conn_iter(self._redis)
            except CancelledError:
                raise
            except BaseException as e:
                logger.error(e)
            finally:
                assert self._redis is not None
                await self._redis.close()
                self._redis = None

            if not self._done.is_set():
                logger.debug(f"Reconnect delay {self._reconnect_delay:.2f}s ...")
                await asyncio_sleep(self._reconnect_delay)

    @property
    def redis(self):
        if self._task is None:
            raise MqNotOpenError("Redis task does not open")
        if self._redis is None:
            raise MqRedisIsNoneError("Redis instance is None")
        return self._redis

    async def exists(self, key: str) -> bool:
        exists = 1 == await self.redis.exists(key)
        logger.info(f"Exists '{key}' -> {exists}")
        return exists

    async def get_bytes(self, key: str) -> bytes:
        value = await self.redis.get(key)
        assert isinstance(value, bytes)
        logger.info(f"Get '{key}' -> {value!r}")
        return value

    async def set_bytes(self, key: str, value: bytes) -> None:
        logger.info(f"Set '{key}' -> {value!r}")
        await self.redis.set(key, value)

    async def get_str(self, key: str) -> str:
        return str(await self.get_bytes(key), encoding="utf8")

    async def set_str(self, key: str, value: str) -> None:
        await self.set_bytes(key, value.encode("utf8"))
