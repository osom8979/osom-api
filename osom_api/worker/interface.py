# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import Any, NamedTuple, Sequence

from osom_api.context.msg import MsgRequest, MsgResponse


class ParameterTuple(NamedTuple):
    name: str
    summary: str
    default: Any


class CommandTuple(NamedTuple):
    command: str
    summary: str
    parameters: Sequence[ParameterTuple]


class WorkerInterface(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def version(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def doc(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def path(self) -> str:
        raise NotImplementedError

    @property
    @abstractmethod
    def cmds(self) -> Sequence[CommandTuple]:
        raise NotImplementedError

    @abstractmethod
    async def open(self, context) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def run(self, data: MsgRequest) -> MsgResponse:
        raise NotImplementedError
