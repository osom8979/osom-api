# -*- coding: utf-8 -*-

from typing import Any, Dict, List


class CommonWorker:
    _args: List[Any]
    _kwargs: Dict[str, Any]

    def __init__(self):
        self._args = list()
        self._kwargs = dict()

    @property
    def version(self) -> str:
        return "0.0.0"

    @property
    def doc(self) -> str:
        return "Common osom worker"

    async def open(self, *args, **kwargs) -> None:
        self._args = list(args)
        self._kwargs = kwargs

    async def close(self) -> None:
        pass

    async def run(self, data: Any) -> Any:
        assert self
        return data
