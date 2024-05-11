# -*- coding: utf-8 -*-

from enum import StrEnum, auto

# noinspection PyProtectedMember
from supabase._async.client import AsyncClient

AutoName = auto


class Tables(StrEnum):
    pass


class Columns(StrEnum):
    pass


class Rpcs(StrEnum):
    pass


class Values(StrEnum):
    pass


class DbMixinBase:
    @property
    def supabase(self) -> AsyncClient:
        raise NotImplementedError
