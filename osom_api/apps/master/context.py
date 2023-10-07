# -*- coding: utf-8 -*-

from argparse import Namespace
from contextlib import asynccontextmanager
from signal import SIGINT, raise_signal

from boto3 import resource as boto3_resource
from fastapi import APIRouter, FastAPI, WebSocket
from overrides import override
from supabase import create_client
from supabase.client import ClientOptions as SupabaseClientOptions

from osom_api.apps.master.config import MasterConfig
from osom_api.logging.logging import logger
from osom_api.mq.client import MqClient, MqClientCallback


class Context(MqClientCallback):
    def __init__(self, args: Namespace):
        self._config = MasterConfig.from_namespace(args)

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
        self._supabase = create_client(
            supabase_url=self._config.supabase_url,
            supabase_key=self._config.supabase_key,
            options=SupabaseClientOptions(
                auto_refresh_token=True,
                persist_session=True,
            ),
        )
        self._s3 = boto3_resource(
            service_name="s3",
            endpoint_url=self._config.s3_endpoint,
            aws_access_key_id=self._config.s3_access,
            aws_secret_access_key=self._config.s3_secret,
            region_name=self._config.s3_region,
        )
        self._s3_bucket = self._config.s3_bucket

    @asynccontextmanager
    async def _lifespan(self, app):
        assert self._app == app
        await self._mq.open()
        yield
        await self._mq.close()

    @staticmethod
    def raise_interrupt_signal() -> None:
        raise_signal(SIGINT)

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
        logger.info("The Redis subscription task is completed")

    def run(self) -> None:
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
        )
