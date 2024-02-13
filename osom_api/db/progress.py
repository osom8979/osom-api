# -*- coding: utf-8 -*-

from datetime import datetime
from math import floor
from typing import Dict, Optional, Union

from fastapi import HTTPException, status
from fastapi.types import BaseModel
from supabase import Client as SupabaseClient

# table
progress = "progress"

# columns
id_ = "id"
owner = "owner"
value = "value"
expired_at = "expired_at"
created_at = "created_at"
updated_at = "updated_at"

# rpc
increase_anonymous_progress_value = "increase_anonymous_progress_value"
progress_id = "progress_id"
increase_value = "increase_value"

# values
null = "null"


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


def latest_anonymous_progress_datetime(supabase: SupabaseClient) -> datetime:
    """
    Latest datetime of the progress for anonymous user.
    """

    response = (
        supabase.table(progress)
        .select(created_at)
        .is_(owner, null)
        .order(created_at, desc=True)
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
    return datetime.fromisoformat(row[created_at])


def insert_anonymous_progress(supabase: SupabaseClient) -> InsertProgressResponse:
    response = supabase.table(progress).insert({}).execute()

    if len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found inserted progress",
        )

    assert len(response.data) == 1
    row = response.data[0]
    return InsertProgressResponse(id=row[id_])


def select_anonymous_progress(
    supabase: SupabaseClient,
    code: str,
) -> SelectProgressResponse:
    response = (
        supabase.table(progress)
        .select(value, created_at, expired_at, updated_at)
        .eq(id_, code)
        .is_(owner, null)
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

    if datetime.fromisoformat(row[expired_at]) < datetime.now().astimezone():
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Expired progress",
        )

    return SelectProgressResponse(
        value=row[value],
        expired_at=row[expired_at],
        created_at=row[created_at],
        updated_at=row[updated_at],
    )


def update_anonymous_progress_value(
    supabase: SupabaseClient,
    code: str,
    body: UpdateProgressRequest,
) -> SelectProgressResponse:
    response = (
        supabase.table(progress)
        .update({value: floor(body.value)})
        .eq(id_, code)
        .is_(owner, null)
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
        value=row[value],
        expired_at=row[expired_at],
        created_at=row[created_at],
        updated_at=row[updated_at],
    )


def increase_progress_value(
    supabase: SupabaseClient,
    code: str,
    body: Optional[IncreaseProgressRequest] = None,
) -> SelectProgressResponse:
    params: Dict[str, Union[str, int]] = {progress_id: code}
    if body is not None and body.value is not None:
        params[increase_value] = floor(body.value)
    response = supabase.rpc(increase_anonymous_progress_value, params).execute()

    if len(response.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found increase progress",
        )

    assert len(response.data) == 1
    row = response.data[0]
    return SelectProgressResponse(
        value=row[value],
        expired_at=row[expired_at],
        created_at=row[created_at],
        updated_at=row[updated_at],
    )


def delete_anonymous_progress(supabase: SupabaseClient, code: str) -> None:
    supabase.table(progress).delete().eq(id_, code).is_(owner, null).execute()
