# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, Response, status
from fastapi.datastructures import Headers
from fastapi.responses import ORJSONResponse

# noinspection PyPackageRequirements
from postgrest.exceptions import APIError


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


async def supabase_exception_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(exc, APIError)
    if not compatible_application_json(request.headers):
        return Response(status_code=status.HTTP_406_NOT_ACCEPTABLE)

    return ORJSONResponse(
        content=dict(
            error=dict(
                code=exc.code,
                details=exc.details,
                hint=exc.hint,
                message=exc.message,
            )
        ),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def add_supabase_exception_handler(api: FastAPI) -> None:
    api.add_exception_handler(APIError, supabase_exception_handler)
