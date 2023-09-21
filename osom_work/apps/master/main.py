# -*- coding: utf-8 -*-

from argparse import Namespace

from fastapi import FastAPI, WebSocket
from uvicorn import run as uvicorn_run

app = FastAPI()


@app.get("/health")
async def health():
    return {}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        await websocket.send_text(f"Message text was: {data}")


def master_main(args: Namespace) -> None:
    assert args is not None

    assert isinstance(args.bind, str)
    assert isinstance(args.port, int)
    assert isinstance(args.timeout, float)

    uvicorn_run(
        app,
        host=args.bind,
        port=args.port,
        server_header=False,
    )
