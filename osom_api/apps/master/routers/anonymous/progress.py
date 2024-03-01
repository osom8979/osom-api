# -*- coding: utf-8 -*-

from typing import Annotated, Optional

from fastapi import APIRouter, Body, Path, Response, status

from osom_api.context.context import CommonContext
from osom_api.db.progress import (
    IncreaseProgressRequest,
    UpdateProgressRequest,
    delete_anonymous_progress,
    increase_progress_value,
    insert_anonymous_progress,
    select_anonymous_progress,
    update_anonymous_progress_value,
)
from osom_api.logging.logging import logger


class AnonymousProgressRouter(APIRouter):
    def __init__(self, context: CommonContext):
        self.context = context
        super().__init__(prefix="/anonymous/progress", tags=["anonymous", "progress"])
        self.add_api_route(
            path="",
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
        logger.info("create_progress....")
        result = await insert_anonymous_progress(self.supabase)
        logger.info(f"Insert progress OK. {result}")
        return result

    async def read_progress(self, code: Annotated[str, Path()]):
        result = await select_anonymous_progress(self.supabase, code)
        logger.info(f"Select progress ({code}) OK. {result}")
        return result

    async def update_progress(
        self,
        code: Annotated[str, Path()],
        body: Annotated[UpdateProgressRequest, Body()],
    ):
        result = await update_anonymous_progress_value(self.supabase, code, body)
        logger.info(f"Update progress ({code}) OK. {result}")
        return result

    async def increase_progress(
        self,
        code: Annotated[str, Path()],
        body: Annotated[Optional[IncreaseProgressRequest], Body()] = None,
    ):
        result = await increase_progress_value(self.supabase, code, body)
        logger.info(f"Increase progress ({code}) OK. {result}")
        return result

    async def delete_progress(self, code: str):
        await delete_anonymous_progress(self.supabase, code)
        logger.info(f"Delete progress ({code}) OK.")
        return Response()
