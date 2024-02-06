# -*- coding: utf-8 -*-

from datetime import datetime
from typing import Optional

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
