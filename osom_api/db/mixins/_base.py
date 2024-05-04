# -*- coding: utf-8 -*-

from abc import ABC

# noinspection PyProtectedMember
from supabase._async.client import AsyncClient


class Tables(ABC):
    pass


class Columns(ABC):
    pass


class Rpcs(ABC):
    pass


class Values(ABC):
    pass


class DbMixinBase:
    @property
    def supabase(self) -> AsyncClient:
        raise NotImplementedError
