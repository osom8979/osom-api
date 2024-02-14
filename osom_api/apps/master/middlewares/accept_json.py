# -*- coding: utf-8 -*-

from fastapi import FastAPI, Response, status
from fastapi.applications import ASGIApp, Receive, Scope, Send
from fastapi.datastructures import Headers


def compatible_application_json(headers: Headers) -> bool:
    accept = headers.get("Accept")
    if not accept:
        # 'None' is considered acceptable.
        return True

    tokens = accept.replace(" ", "").lower().split(",")
    for token in tokens:
        mime = token.split(";")[0]
        if mime in ("application/json", "application/*", "*/*"):
            return True

    return False


class AcceptJsonMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            if not compatible_application_json(Headers(scope=scope)):
                response = Response(status_code=status.HTTP_406_NOT_ACCEPTABLE)
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)

    @classmethod
    def inject(cls, api: FastAPI) -> None:
        # noinspection PyTypeChecker
        api.add_middleware(cls)


def add_accept_json_middleware(api: FastAPI) -> None:
    AcceptJsonMiddleware.inject(api)
