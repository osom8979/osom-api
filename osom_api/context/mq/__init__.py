# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from asyncio import Event, Task, create_task, get_running_loop, run_coroutine_threadsafe
from asyncio.exceptions import CancelledError, TimeoutError
from asyncio.timeouts import timeout as async_timeout
from datetime import datetime
from os import R_OK, access, path
from typing import Literal, Optional, Sequence

from redis.asyncio import from_url
from redis.asyncio.client import PubSub

from osom_api.aio.shield_any import shield_any
from osom_api.arguments import (
    DEFAULT_REDIS_CLOSE_TIMEOUT,
    DEFAULT_REDIS_CONNECTION_TIMEOUT,
    DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
)
from osom_api.arguments import VERBOSE_LEVEL_1 as VL1
from osom_api.arguments import VERBOSE_LEVEL_2 as VL2
from osom_api.context.mq.message import Message
from osom_api.context.mq.path import BROADCAST_PATH, encode_path
from osom_api.logging.logging import logger

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
    async def on_mq_done(self) -> None:
        raise NotImplementedError


class MqClient:
    _task: Optional[Task[None]]
    _subscribe_begin: Optional[datetime]

    def __init__(
        self,
        url: Optional[str] = None,
        connection_timeout=DEFAULT_REDIS_CONNECTION_TIMEOUT,
        subscribe_timeout=DEFAULT_REDIS_SUBSCRIBE_TIMEOUT,
        close_timeout=DEFAULT_REDIS_CLOSE_TIMEOUT,
        callback: Optional[MqClientCallback] = None,
        done: Optional[Event] = None,
        task_name: Optional[str] = None,
        ssl_cert_reqs: Literal["none", "optional", "required"] = "none",
        debug=False,
        verbose=0,
    ):
        self._redis = from_url(
            url,
            socket_connect_timeout=connection_timeout,
            ssl_cert_reqs=ssl_cert_reqs,
        )
        self._subscribe_timeout = subscribe_timeout
        self._close_timeout = close_timeout
        self._callback = callback
        self._done = done if done is not None else Event()
        self._task_name = task_name if task_name else self.__class__.__name__
        self._task = None
        self._subscribe_begin = None
        self._debug = debug
        self._verbose = verbose

    async def open(self) -> None:
        assert self._task is None
        self._done.clear()
        self._task = create_task(self._redis_main(), name=self._task_name)
        self._task.add_done_callback(self._task_done)

    async def close(self) -> None:
        assert self._task is not None
        self._done.set()

        if not self._task.cancelled() and self._subscribe_begin is not None:
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
                await pubsub.close()
        except CancelledError:
            raise
        except BaseException as e:
            logger.error(e)
        finally:
            await self._redis.close()

    async def _redis_subscribe_main(self, pubsub: PubSub) -> None:
        subscribe_paths = (encode_path(BROADCAST_PATH),)

        logger.debug("Requesting a subscription ...")
        await pubsub.subscribe(*subscribe_paths)
        logger.info("Subscription completed!")

        if self._debug:
            logger.info(f"Subscription paths: {subscribe_paths}")

        while not self._done.is_set():
            if self._debug and self._verbose >= VL2:
                logger.debug(f"Subscription message ... {self._subscribe_timeout:.1f}s")

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
            logger.debug(f"Data was received on channel {channel} -> {data}")

            if self._callback is not None:
                await shield_any(self._callback.on_mq_subscribe(channel, data), logger)

    async def ping(self, timeout: Optional[float] = None) -> bool:
        try:
            async with async_timeout(timeout):
                await self._redis.ping()
        except:  # noqa
            return False
        else:
            return True

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

    async def lpush_bytes(
        self, key: str, value: bytes, expire: Optional[int] = None
    ) -> None:
        if expire is not None:
            logger.info(f"Left PUSH '{key}' -> {value!r} (expire: {expire}s)")
            async with self._redis.pipeline(transaction=True) as pipeline:
                await pipeline.lpush(key, value).expire(key, expire).execute()
        else:
            logger.info(f"Left PUSH '{key}' -> {value!r}")
            await self._redis.lpush(key, value)

    async def brpop_bytes(
        self,
        key: str,
        timeout: Optional[int] = None,
    ) -> Optional[Sequence[bytes]]:
        logger.debug(f"Blocking Right POP '{key}' {timeout}s ...")
        value = await self._redis.brpop(key, timeout)

        if value is None:
            logger.debug(f"Blocking Right POP '{key}' ... timeout!")
            return None

        assert isinstance(value, tuple)
        assert len(value) % 2 == 0 and len(value) >= 2
        logger.info(f"Blocking Right POP '{key}' -> {value}")
        return value
