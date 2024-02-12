# -*- coding: utf-8 -*-

from typing import Annotated, Optional

from fastapi import APIRouter, Form, Path, Response, status
from fastapi.exceptions import HTTPException

# noinspection PyPackageRequirements
from postgrest.exceptions import APIError

from osom_api.common.context import CommonContext
from osom_api.db.progress import (
    delete_anonymous_progress,
    increase_progress_value,
    insert_anonymous_progress,
    select_anonymous_progress,
)
from osom_api.logging.logging import logger


class ProgressRouter(APIRouter):
    def __init__(self, context: CommonContext):
        self.context = context
        super().__init__(prefix="/progress")
        self.add_api_route(
            path="/",
            endpoint=self.create_progress,
            methods=["PUT"],
            status_code=status.HTTP_201_CREATED,
        )
        self.add_api_route(
            path="/{code}",
            endpoint=self.read_progress,
            methods=["GET"],
        )
        self.add_api_route(
            path="/{code}",
            endpoint=self.update_progress,
            methods=["POST"],
        )
        self.add_api_route(
            path="/{code}/increase",
            endpoint=self.increase_progress,
            methods=["POST"],
        )
        self.add_api_route(
            path="/{code}",
            endpoint=self.delete_progress,
            methods=["DELETE"],
        )

    @property
    def mq(self):
        return self.context.mq

    @property
    def supabase(self):
        return self.context.supabase

    @property
    def s3(self):
        return self.context.s3

    async def create_progress(self):
        try:
            code = insert_anonymous_progress(self.supabase)
        except BaseException as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

        if code is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Anonymous progress insertion error",
            )

        logger.info(f"Insert progress ({code})")
        return dict(id=code)

    async def read_progress(self, code: Annotated[str, Path()]):
        try:
            result = select_anonymous_progress(self.supabase, code)
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.json(),
            )

        logger.info(f"Read progress ({code}) {result}")
        return result

    async def update_progress(self, code: str):
        raise NotImplementedError

    async def increase_progress(
        self,
        code: str,
        value: Annotated[Optional[int], Form()] = None,
    ):
        try:
            result = increase_progress_value(self.supabase, code, value)
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.json(),
            )

        logger.info(f"Increase progress ({code}) {result}")
        return result

    async def delete_progress(self, code: str):
        try:
            delete_anonymous_progress(self.supabase, code)
        except APIError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.json(),
            )

        logger.info(f"Delete progress ({code})")
        return Response()
