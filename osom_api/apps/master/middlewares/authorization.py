# -*- coding: utf-8 -*-

from typing import Optional

from fastapi import Response, status
from fastapi.applications import ASGIApp, Receive, Scope, Send
from fastapi.datastructures import Headers


def get_authorization_param(headers: Headers) -> Optional[str]:
    authorization = headers.get("Authorization")
    if not authorization:
        return None

    scheme, _, param = authorization.partition(" ")
    if scheme.strip().lower() != "bearer":
        return None

    return param.strip()


class AuthorizationMiddleware:
    def __init__(self, app: ASGIApp, token: Optional[str] = None) -> None:
        self.app = app
        self.token = token

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if self.token and scope["type"] == "http":
            param = get_authorization_param(Headers(scope=scope))
            if not param or param != self.token:
                response = Response(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
