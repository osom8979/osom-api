# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from asyncio import Event, Task, create_task, get_running_loop, run_coroutine_threadsafe
from asyncio.exceptions import CancelledError, TimeoutError
from asyncio.timeouts import timeout as async_timeout
from datetime import datetime
from os import R_OK, access, path
from typing import Any, Dict, Literal, Optional, Sequence, Union

from redis.asyncio import from_url
from redis.asyncio.client import PubSub, Redis
from redis.exceptions import RedisError

from osom_api.aio.shield_any import shield_any
from osom_api.args.redis import RedisArgs
from osom_api.arguments import (
    DEFAULT_REDIS_CLOSE_TIMEOUT,
    DEFAULT_REDIS_EXPIRE_LONG,
    DEFAULT_REDIS_EXPIRE_MEDIUM,
    DEFAULT_REDIS_EXPIRE_SHORT,
    DEFAULT_REDIS_SSL_CERT_REQS,
    REDIS_SSL_CERT_REQS,
)
from osom_api.arguments import VERBOSE_LEVEL_1 as VL1
from osom_api.arguments import VERBOSE_LEVEL_2 as VL2
from osom_api.context.mq.message import Message
from osom_api.exceptions import NotInitializedError
from osom_api.logging.logging import logger
from osom_api.paths import MQ_BROADCAST_PATH
from osom_api.utils.path.mq import encode_path

SslCertReqs = Literal["none", "optional", "required"]


def validation_redis_file(name: str, file: Optional[str] = None) -> None:
    if not file:
        raise ValueError(f"Redis TLS {name} file is not defined")
    elif not path.exists(file):
        raise FileNotFoundError(f"Redis TLS {name} file is not exists")
    elif not path.isfile(file):
        raise FileNotFoundError(f"Redis TLS {name} file is not file type")
    elif not access(file, R_OK):
        raise PermissionError(f"Redis TLS {name} file is not readable")


class MqClientCallback(metaclass=ABCMeta):
    @abstractmethod
    async def on_mq_connect(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_mq_closing(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def on_mq_done(self) -> None:
        raise NotImplementedError


class MqClient:
    _redis: Optional[Redis]
    _task: Optional[Task[None]]
    _subscribe_begin: Optional[datetime]

    def __init__(
        self,
        url: Optional[str] = None,
        connection_timeout: Optional[float] = None,
        subscribe_timeout: Optional[float] = None,
        close_timeout: Optional[float] = DEFAULT_REDIS_CLOSE_TIMEOUT,
        expire_short: Optional[float] = DEFAULT_REDIS_EXPIRE_SHORT,
        expire_medium: Optional[float] = DEFAULT_REDIS_EXPIRE_MEDIUM,
        expire_long: Optional[float] = DEFAULT_REDIS_EXPIRE_LONG,
        callback: Optional[MqClientCallback] = None,
        done: Optional[Event] = None,
        task_name: Optional[str] = None,
        ssl_cert_reqs: Optional[str] = DEFAULT_REDIS_SSL_CERT_REQS,
        subscribe_paths: Optional[Sequence[Union[str, bytes]]] = None,
        debug=False,
        verbose=0,
    ):
        if url:
            options: Dict[str, Any] = dict()
            if connection_timeout is not None:
                options["socket_connect_timeout"] = connection_timeout
            if url.startswith("rediss://") and ssl_cert_reqs:
                if ssl_cert_reqs not in REDIS_SSL_CERT_REQS:
                    raise RedisError(
                        f"Invalid SSL certificate requirements flag: {ssl_cert_reqs}"
                    )
                options["ssl_cert_reqs"] = ssl_cert_reqs
            self._redis = from_url(url, **options)
        else:
            self._redis = None

        self._subscribe_timeout = subscribe_timeout
        self._close_timeout = close_timeout
        self._expire_short = expire_short
        self._expire_medium = expire_medium
        self._expire_long = expire_long
        self._callback = callback
        self._done = done if done is not None else Event()
        self._debug = debug
        self._verbose = verbose

        self._task = None
        self._task_name = task_name if task_name else self.__class__.__name__

        self._subscribe_begin = None
        self._subscribe_paths = set()
        if subscribe_paths:
            for sp in subscribe_paths:
                if isinstance(sp, str):
                    self._subscribe_paths.add(encode_path(sp))
                elif isinstance(sp, bytes):
                    self._subscribe_paths.add(sp)
                else:
                    raise TypeError(f"Unexpected type {type(sp).__name__}")
        else:
            self._subscribe_paths.add(encode_path(MQ_BROADCAST_PATH))

    @classmethod
    def from_args(
        cls,
        args: RedisArgs,
        *,
        mq_callback: Optional[MqClientCallback] = None,
        mq_asyncio_event: Optional[Event] = None,
        mq_task_name: Optional[str] = None,
        mq_subscribe_paths: Optional[Sequence[Union[str, bytes]]] = None,
    ):
        return cls(
            url=args.redis_url,
            connection_timeout=args.redis_connection_timeout,
            subscribe_timeout=args.redis_subscribe_timeout,
            close_timeout=args.redis_close_timeout,
            expire_short=args.redis_expire_short,
            expire_medium=args.redis_expire_medium,
            expire_long=args.redis_expire_long,
            callback=mq_callback,
            done=mq_asyncio_event,
            task_name=mq_task_name,
            ssl_cert_reqs=args.redis_ssl_cert_reqs,
            subscribe_paths=mq_subscribe_paths,
            debug=args.debug,
            verbose=args.verbose,
        )

    @property
    def redis(self):
        if self._redis is None:
            raise NotInitializedError("Redis is not initialized")
        return self._redis

    async def open(self) -> None:
        if self._redis is None:
            logger.warning("Redis is not initialized. Cancels the open operation.")
            return

        assert self._task is None
        self._done.clear()
        self._task = create_task(self._redis_main(), name=self._task_name)
        self._task.add_done_callback(self._task_done)

    async def close(self) -> None:
        if self._redis is None:
            logger.warning("Redis is not initialized. Cancels the close operation.")
            return

        assert self._task is not None
        self._done.set()

        if (
            not self._task.cancelled()
            and self._subscribe_begin is not None
            and self._subscribe_timeout is not None
            and self._close_timeout is not None
        ):
            # If the waiting time is longer than the close timeout,
            # Forcefully cancels the task.
            # This will prevent the shutdown wait time from becoming too long.
            duration = (datetime.now() - self._subscribe_begin).total_seconds()
            expected_waiting_time = self._subscribe_timeout - duration
            if self._close_timeout < expected_waiting_time:
                if self._debug:
                    logger.warning("Forces cancellation of a task during Redis close")
                    if self._verbose >= VL1:
                        logger.warning(
                            f"Close timeout ({self._close_timeout:.1f}s) vs "
                            f"Expected waiting time ({expected_waiting_time:.1f}s)"
                        )
                self._task.cancel()

        try:
            async with async_timeout(self._close_timeout):
                await self._task
        except TimeoutError as e:
            self._task.set_exception(e)
            self._task.cancel("Raise close timeout exception")

    def _task_done(self, task) -> None:
        assert self._task == task
        if self._callback is None:
            return

        try:
            run_coroutine_threadsafe(self._callback.on_mq_done(), get_running_loop())
        except BaseException as e:  # noqa
            logger.exception(e)

    async def _redis_main(self) -> None:
        assert self._redis is not None

        try:
            logger.debug("Redis PING ...")
            await self._redis.ping()
        except BaseException as e:
            logger.error(f"Redis PING error: {e}")
            raise
        else:
            logger.info("Redis PING->PONG!")

        if self._callback is not None:
            await self._callback.on_mq_connect()

        try:
            pubsub = self._redis.pubsub()
            try:
                await self._redis_subscribe_main(pubsub)
            finally:
                if self._callback is not None:
                    await shield_any(self._callback.on_mq_closing(), logger)
                await pubsub.close()
        except CancelledError:
            logger.warning("A cancellation signal was detected in a Redis Task")
        except BaseException as e:
            logger.error(e)
        finally:
            await self._redis.close()

    async def _redis_subscribe_main(self, pubsub: PubSub) -> None:
        logger.debug("Requesting a subscription ...")
        await pubsub.subscribe(*self._subscribe_paths)
        logger.info("Subscription completed!")

        if self._debug:
            logger.info(f"Subscription paths: {self._subscribe_paths}")

        while not self._done.is_set():
            if self._debug and self._verbose >= VL2:
                if self._subscribe_timeout is not None:
                    subscribe_timeout_text = f" {self._subscribe_timeout:.1f}s"
                else:
                    subscribe_timeout_text = ""
                logger.debug(f"Subscription message ...{subscribe_timeout_text}")

            try:
                self._subscribe_begin = datetime.now()
                msg = await pubsub.get_message(
                    ignore_subscribe_messages=True,
                    timeout=self._subscribe_timeout,
                )
            finally:
                self._subscribe_begin = None

            if msg is None:
                if self._debug and self._verbose >= VL2:
                    logger.debug("Subscription message not received")
                continue

            if self._debug and self._verbose >= VL1:
                logger.debug(f"Recv subscription message: {msg}")

            msg = Message.from_message(msg)
            if not msg.is_message:
                continue

            channel = msg.channel
            data = msg.data
            if self._debug:
                logger.debug(f"Data was received on channel {channel} -> {data}")

            if self._callback is not None:
                await shield_any(self._callback.on_mq_subscribe(channel, data), logger)

    async def publish(self, key: str, data: bytes) -> None:
        logger.info(f"Publish '{key}' -> {data!r}")
        await self.redis.publish(key, data)

    async def ping(self, timeout: Optional[float] = None) -> bool:
        try:
            async with async_timeout(timeout):
                await self.redis.ping()
        except:  # noqa
            return False
        else:
            return True

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

    async def lpush_bytes(
        self, key: str, value: bytes, expire: Optional[int] = None
    ) -> None:
        if expire is not None:
            logger.info(f"Left PUSH '{key}' -> {value!r} (expire: {expire}s)")
            async with self.redis.pipeline(transaction=True) as pipeline:
                # noinspection PyUnresolvedReferences
                await pipeline.lpush(key, value).expire(key, expire).execute()
        else:
            logger.info(f"Left PUSH '{key}' -> {value!r}")
            await self.redis.lpush(key, value)

    async def brpop_bytes(
        self,
        key: str,
        timeout: Optional[int] = None,
    ) -> Optional[Sequence[bytes]]:
        logger.debug(f"Blocking Right POP '{key}' {timeout}s ...")
        value = await self.redis.brpop([key], timeout)

        if value is None:
            logger.debug(f"Blocking Right POP '{key}' ... timeout!")
            return None

        assert isinstance(value, tuple)
        assert len(value) % 2 == 0 and len(value) >= 2
        logger.info(f"Blocking Right POP '{key}' -> {value}")
        return value
