# -*- coding: utf-8 -*-

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import ORJSONResponse

# noinspection PyPackageRequirements
from postgrest.exceptions import APIError

from osom_api.apps.master.exception_handlers.error_object import create_error_object


async def supabase_exception_handler(request: Request, exc: Exception) -> Response:
    assert isinstance(request, Request)
    assert isinstance(exc, APIError)

    error_object = create_error_object(
        exc.code,
        exc.details,
        exc.hint,
        exc.message,
    )

    return ORJSONResponse(
        content=dict(error=error_object),
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


def add_supabase_exception_handler(api: FastAPI) -> None:
    api.add_exception_handler(APIError, supabase_exception_handler)
