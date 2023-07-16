# -*- coding: utf-8 -*-

from contextlib import asynccontextmanager

from aioredis import Redis
from aioredis import from_url as aioredis_from_url
from fastapi import FastAPI


class MasterContext:
    redis: Redis

    def __init__(
        self,
        redis_host="localhost",
        redis_user="osom",
        redis_pass="work",
    ):
        self.redis_host = redis_host
        self.redis_user = redis_user
        self.redis_pass = redis_pass

    async def open(self) -> None:
        self.redis = await aioredis_from_url(
            f"redis://{self.redis_host}",
            username=self.redis_user,
            password=self.redis_pass,
        )

    async def close(self) -> None:
        await self.redis.close()


@asynccontextmanager
async def context_lifespan(app: FastAPI):
    context = MasterContext()
    await context.open()
    yield
    await context.close()
