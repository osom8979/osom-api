# -*- coding: utf-8 -*-

from datetime import datetime
from math import floor
from typing import Dict, Optional, Union

from fastapi import HTTPException, status
from fastapi.types import BaseModel

from osom_api.context.db.mixins._base import (
    AutoName,
    Columns,
    DbMixinBase,
    Rpcs,
    Tables,
    Values,
)


class T(Tables):
    progress = AutoName()


class C(Columns):
    id = AutoName()
    owner = AutoName()
    value = AutoName()  # type: ignore[assignment]
    expired_at = AutoName()
    created_at = AutoName()
    updated_at = AutoName()


class R(Rpcs):
    increase_anonymous_progress_value = AutoName()
    progress_id = AutoName()
    increase_value = AutoName()


class V(Values):
    null = AutoName()


class InsertProgressResponse(BaseModel):
    id: str


class SelectProgressResponse(BaseModel):
    value: float
    expired_at: str
    created_at: str
    updated_at: Optional[str] = None


class UpdateProgressRequest(BaseModel):
    value: float


class IncreaseProgressRequest(BaseModel):
    value: Optional[float] = None


class Progress(DbMixinBase):
    async def latest_anonymous_progress_datetime(self) -> datetime:
        """
        Latest datetime of the progress for anonymous user.
        """
        response = (
            await self.supabase.table(T.progress)
            .select(C.created_at)
            .is_(C.owner, V.null)
            .order(C.created_at, desc=True)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found latest progress",
            )

        assert len(response.data) == 1
        row = response.data[0]
        return datetime.fromisoformat(row[C.created_at])

    async def insert_anonymous_progress(self) -> InsertProgressResponse:
        response = await self.supabase.table(T.progress).insert({}).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found inserted progress",
            )

        assert len(response.data) == 1
        row = response.data[0]
        return InsertProgressResponse(id=row[C.id])

    async def select_anonymous_progress(self, code: str) -> SelectProgressResponse:
        response = (
            await self.supabase.table(T.progress)
            .select(C.value, C.created_at, C.expired_at, C.updated_at)
            .eq(C.id, code)
            .is_(C.owner, V.null)
            .limit(1)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found selected progress",
            )

        assert len(response.data) == 1
        row = response.data[0]

        if datetime.fromisoformat(row[C.expired_at]) < datetime.now().astimezone():
            raise HTTPException(
                status_code=status.HTTP_410_GONE,
                detail="Expired progress",
            )

        return SelectProgressResponse(
            value=row[C.value],
            expired_at=row[C.expired_at],
            created_at=row[C.created_at],
            updated_at=row[C.updated_at],
        )

    async def update_anonymous_progress_value(
        self,
        code: str,
        body: UpdateProgressRequest,
    ) -> SelectProgressResponse:
        response = (
            await self.supabase.table(T.progress)
            .update({C.value: floor(body.value)})
            .eq(C.id, code)
            .is_(C.owner, V.null)
            .execute()
        )

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found updated progress",
            )

        assert len(response.data) == 1
        row = response.data[0]
        return SelectProgressResponse(
            value=row[C.value],
            expired_at=row[C.expired_at],
            created_at=row[C.created_at],
            updated_at=row[C.updated_at],
        )

    async def increase_progress_value(
        self,
        code: str,
        body: Optional[IncreaseProgressRequest] = None,
    ) -> SelectProgressResponse:
        params: Dict[str, Union[str, int]] = {R.progress_id: code}
        if body is not None and body.value is not None:
            params[R.increase_value] = floor(body.value)
        response = await self.supabase.rpc(
            R.increase_anonymous_progress_value, params
        ).execute()

        if len(response.data) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Not found increase progress",
            )

        assert len(response.data) == 1
        row = response.data[0]
        return SelectProgressResponse(
            value=row[C.value],
            expired_at=row[C.expired_at],
            created_at=row[C.created_at],
            updated_at=row[C.updated_at],
        )

    async def delete_anonymous_progress(self, code: str):
        response = (
            await self.supabase.table(T.progress)
            .delete()
            .eq(C.id, code)
            .is_(C.owner, V.null)
            .execute()
        )
        return response
