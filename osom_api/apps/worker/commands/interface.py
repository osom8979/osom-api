# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any
from weakref import ref

from overrides import override

from osom_api.common.context import CommonContext


class WorkerCommandInterface(metaclass=ABCMeta):
    @abstractmethod
    async def run(self, data: Any) -> Any:
        raise NotImplementedError


class WorkerCommand(WorkerCommandInterface):
    def __init__(self, context: CommonContext):
        self._context = ref(context)

    @property
    def context(self) -> CommonContext:
        context = self._context()
        if context is None:
            raise RuntimeError("The context reference is broken")
        return context

    @property
    def mq(self):
        return self.context.mq

    @property
    def supabase(self):
        return self.context.supabase

    @property
    def s3(self):
        return self.context.s3

    @override
    async def run(self, data: Any) -> Any:
        raise NotImplementedError
