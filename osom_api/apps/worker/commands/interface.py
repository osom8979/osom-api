# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any
from weakref import ref

from overrides import override

from osom_api.context import Context


class WorkerCommandInterface(metaclass=ABCMeta):
    @property
    @abstractmethod
    def command(self) -> str:
        raise NotImplementedError

    @abstractmethod
    async def run(self, data: Any) -> Any:
        raise NotImplementedError


class WorkerCommand(WorkerCommandInterface):
    def __init__(self, context: Context):
        self._context = ref(context)

    @property
    def context(self) -> Context:
        context = self._context()
        if context is None:
            raise RuntimeError("The context reference is broken")
        return context

    @property
    @override
    def command(self) -> str:
        raise NotImplementedError

    @override
    async def run(self, data: Any) -> Any:
        raise NotImplementedError
