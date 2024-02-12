# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Dict, Optional, Union

# noinspection PyPackageRequirements
from pydantic import BaseModel
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

# values
null = "null"


class AnonymousProgressRow(BaseModel):
    value: float
    expired_at: datetime
    created_at: datetime
    updated_at: datetime


def latest_anonymous_progress_datetime(supabase: SupabaseClient) -> Optional[datetime]:
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
        return None

    assert len(response.data) == 1
    return datetime.fromisoformat(response.data[0][created_at])


def insert_anonymous_progress(supabase: SupabaseClient) -> Optional[str]:
    response = supabase.table(progress).insert({}).execute()

    if len(response.data) == 0:
        return None

    assert len(response.data) == 1
    return response.data[0][id_]


def increase_progress_value(
    supabase: SupabaseClient,
    code: str,
    increase_value: Optional[int] = None,
) -> Optional[AnonymousProgressRow]:
    params: Dict[str, Union[str, int]] = {"progress_id": code}
    if increase_value:
        params["increase_value"] = increase_value
    response = supabase.rpc("increase_progress_value", params).execute()

    if len(response.data) == 0:
        return None

    assert len(response.data) == 1
    row = response.data[0]
    return AnonymousProgressRow(
        value=row[value],
        expired_at=row[expired_at],
        created_at=row[created_at],
        updated_at=row[updated_at],
    )


def select_anonymous_progress(
    supabase: SupabaseClient,
    code: str,
) -> Optional[AnonymousProgressRow]:
    response = (
        supabase.table(progress)
        .select(value, created_at, expired_at, updated_at)
        .eq(id_, code)
        .is_(owner, null)
        .lt(expired_at, "NOW()")
        .limit(1)
        .execute()
    )

    if len(response.data) == 0:
        return None

    assert len(response.data) == 1
    row = response.data[0]
    return AnonymousProgressRow(
        value=row[value],
        expired_at=row[expired_at],
        created_at=row[created_at],
        updated_at=row[updated_at],
    )


def delete_anonymous_progress(supabase: SupabaseClient, code: str) -> None:
    supabase.table(progress).delete().eq(id_, code).execute()
