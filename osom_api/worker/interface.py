# -*- coding: utf-8 -*-

from abc import ABC, abstractmethod
from typing import List

from osom_api.msg import MsgRequest, MsgResponse
from osom_api.worker.descs import CmdDesc


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
    def cmds(self) -> List[CmdDesc]:
        raise NotImplementedError

    @abstractmethod
    def init(self, *args) -> None:
        raise NotImplementedError

    @abstractmethod
    async def open(self, context) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def run(self, request: MsgRequest) -> MsgResponse:
        raise NotImplementedError
