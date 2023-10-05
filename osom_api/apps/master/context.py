# -*- coding: utf-8 -*-

from argparse import Namespace
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI, WebSocket

from osom_api.apps.master.config import Config


class Context:
    def __init__(self, args: Namespace):
        self._config = Config.from_namespace(args)

        self._router = APIRouter()
        self._router.add_api_route("/health", self.health, methods=["GET"])
        self._router.add_api_websocket_route("/ws", self.ws)

        self._app = FastAPI(lifespan=self._lifespan)
        self._app.include_router(self._router)

    @asynccontextmanager
    async def _lifespan(self, app):
        assert self._app == app
        # open
        yield
        # close

    async def health(self):
        assert self
        return {}

    async def ws(self, websocket: WebSocket) -> None:
        assert self
        await websocket.accept()
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Message text was: {data}")

    def run(self) -> None:
        from uvicorn import run as uvicorn_run

        uvicorn_run(
            self._app,
            host=self._config.http_host,
            port=self._config.http_port,
            loop=self._config.loop_setup_type,
            lifespan="on",
            proxy_headers=False,
            server_header=False,
            date_header=False,
        )
