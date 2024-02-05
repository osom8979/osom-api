# -*- coding: utf-8 -*-

from argparse import Namespace
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, WebSocket
from overrides import override

from osom_api.apps.master.config import MasterConfig
from osom_api.common.context import CommonContext
from osom_api.logging.logging import logger


class MasterContext(CommonContext):
    def __init__(self, args: Namespace):
        self._config = MasterConfig.from_namespace(args)
        self._config.logging_params()

        super().__init__(self._config)

        self._router = APIRouter()
        self._router.add_api_route("/health", self.health, methods=["GET"])
        self._router.add_api_websocket_route("/ws", self.ws)

        self._app = FastAPI(lifespan=self._lifespan)
        self._app.include_router(self._router)

    @asynccontextmanager
    async def _lifespan(self, app):
        assert self._app == app
        await self.common_open()
        yield
        await self.common_close()

    async def health(self):
        assert self
        return {}

    async def ws(self, websocket: WebSocket) -> None:
        assert self
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")

    @override
    async def on_mq_connect(self) -> None:
        logger.info("Connection to redis was successful!")

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        logger.info(f"Recv sub msg channel: {channel!r} -> {data!r}")

    @override
    async def on_mq_done(self) -> None:
        logger.warning("Redis task is done")

    def run(self) -> None:
        # noinspection PyPackageRequirements
        from uvicorn import run as uvicorn_run

        uvicorn_run(
            self._app,
            host=self._config.http_host,
            port=self._config.http_port,
            loop=self._config.loop_setup_type,
            lifespan="on",
            log_config=None,
            log_level=None,
            access_log=True,
            proxy_headers=False,
            server_header=False,
            date_header=False,
            forwarded_allow_ips="*",
        )
