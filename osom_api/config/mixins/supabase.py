# -*- coding: utf-8 -*-

from typing import Optional


class SupabaseProps:
    supabase_url: Optional[str]
    supabase_key: Optional[str]
    supabase_postgrest_timeout: float
    supabase_storage_timeout: float

    def assert_supabase_properties(self) -> None:
        assert isinstance(self.supabase_url, (type(None), str))
        assert isinstance(self.supabase_key, (type(None), str))
        assert isinstance(self.supabase_postgrest_timeout, float)
        assert isinstance(self.supabase_storage_timeout, float)
