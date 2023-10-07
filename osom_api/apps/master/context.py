# -*- coding: utf-8 -*-

from argparse import Namespace
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, WebSocket
from overrides import override

from osom_api.apps.master.config import Config
from osom_api.mq.client import MqClient, MqClientCallback


class Context(MqClientCallback):
    def __init__(self, args: Namespace):
        self._config = Config.from_namespace(args)

        self._router = APIRouter()
        self._router.add_api_route("/health", self.health, methods=["GET"])
        self._router.add_api_websocket_route("/ws", self.ws)

        self._app = FastAPI(lifespan=self._lifespan)
        self._app.include_router(self._router)

        self._mq = MqClient(
            host=self._config.redis_host,
            port=self._config.redis_port,
            database=self._config.redis_database,
            password=self._config.redis_password,
            use_tls=self._config.redis_use_tls,
            ca_cert_path=self._config.redis_ca_cert,
            cert_path=self._config.redis_cert,
            key_path=self._config.redis_key,
            connection_timeout=self._config.redis_connection_timeout,
            subscribe_timeout=self._config.redis_subscribe_timeout,
            close_timeout=self._config.redis_close_timeout,
            callback=self,
            done=None,
            task_name=None,
            debug=self._config.debug,
            verbose=self._config.verbose,
        )

    @asynccontextmanager
    async def _lifespan(self, app):
        assert self._app == app
        await self._mq.open()
        yield
        await self._mq.close()

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
        pass

    @override
    async def on_mq_subscribe(self, channel: bytes, data: bytes) -> None:
        pass

    @override
    async def on_mq_done(self) -> None:
        pass

    def run(self) -> None:
        from uvicorn import run as uvicorn_run

        uvicorn_run(
            self._app,
            host=self._config.http_host,
            port=self._config.http_port,
            loop=self._config.loop_setup_type,
            lifespan="on",
            log_level=self._config.severity,
            access_log=True,
            proxy_headers=False,
            server_header=False,
            date_header=False,
        )
