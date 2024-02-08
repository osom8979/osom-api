# -*- coding: utf-8 -*-

from typing import Optional

from starlette.datastructures import Headers
from starlette.responses import Response
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.types import ASGIApp, Receive, Scope, Send


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
                    status_code=HTTP_401_UNAUTHORIZED,
                    headers={"WWW-Authenticate": "Bearer"},
                )
                await response(scope, receive, send)
                return

        await self.app(scope, receive, send)
