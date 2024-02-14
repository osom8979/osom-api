# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse

# noinspection PyPackageRequirements
from postgrest.exceptions import APIError


async def supabase_exception_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(request, Request)
    assert isinstance(exc, APIError)
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
