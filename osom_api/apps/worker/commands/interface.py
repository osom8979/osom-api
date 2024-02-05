# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from typing import Any

from osom_api.common.context import CommonContext


class WorkerCommand(metaclass=ABCMeta):
    __api__: str

    @abstractmethod
    async def run(self, data: Any, context: CommonContext) -> Any:
        raise NotImplementedError
