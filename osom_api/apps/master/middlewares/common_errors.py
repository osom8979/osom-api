# -*- coding: utf-8 -*-

from fastapi import status
from fastapi.applications import ASGIApp, Receive, Scope, Send
from fastapi.exceptions import HTTPException

# noinspection PyPackageRequirements
from postgrest.exceptions import APIError


class CommonErrorsMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        try:
            await self.app(scope, receive, send)
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.json(),
            )
