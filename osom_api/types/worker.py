# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import NamedTuple, Sequence

from osom_api.context.msg import MsgRequest, MsgResponse


class Arg(NamedTuple):
    key: str
    summary: str


class Cmd(NamedTuple):
    command: str
    summary: str
    arguments: Sequence[Arg]


class WorkerInterface(ABC):
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
    def cmd(self) -> Sequence[Cmd]:
        raise NotImplementedError

    @abstractmethod
    async def open(self, *args, **kwargs) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def run(self, data: MsgRequest) -> MsgResponse:
        raise NotImplementedError
