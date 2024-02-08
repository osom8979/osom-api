# -*- coding: utf-8 -*-

from typing import Optional

from fastapi import APIRouter
from fastapi.exceptions import HTTPException
from postgrest.exceptions import APIError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR

from osom_api.common.context import CommonContext
from osom_api.db.progress import increase_progress_value, insert_anonymous_progress
from osom_api.logging.logging import logger


class ProgressRouter(APIRouter):
    def __init__(self, context: CommonContext):
        self.context = context
        super().__init__(prefix="/progress")
        self.add_api_route("/create", self.create, methods=["POST"])
        self.add_api_route("/increase", self.increase, methods=["GET"])

    @property
    def mq(self):
        return self.context.mq

    @property
    def supabase(self):
        return self.context.supabase

    @property
    def s3(self):
        return self.context.s3

    async def create(self):
        try:
            progress_id = insert_anonymous_progress(self.supabase)
        except BaseException as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=str(e),
            )

        if progress_id is None:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Anonymous progress insertion error",
            )

        logger.info(f"Insert progress ID: {progress_id}")
        return dict(id=progress_id)

    async def increase(self, progress_id: str, increase_value: Optional[int] = None):
        try:
            value = increase_progress_value(self.supabase, progress_id, increase_value)
        except APIError as e:
            raise HTTPException(
                status_code=HTTP_500_INTERNAL_SERVER_ERROR,
                detail=e.json(),
            )

        logger.info(f"Increase progress ({progress_id}) value: {value}")
        return dict(value=value)
