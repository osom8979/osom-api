# -*- coding: utf-8 -*-

from typing import Annotated

from osom_api.arguments import version as osom_version
from osom_api.worker.base import WorkerBase
from osom_api.worker.metas import ParamMeta


class TesterWorker(WorkerBase):
    def __init__(self):
        super().__init__("test", osom_version(), "Test worker")
        self.register_command(self.on_tester)

    async def on_tester(
        self,
        p1: Annotated[int, ParamMeta(doc="meta1")] = 1,
        p2: Annotated[str, ParamMeta(doc="meta2")] = "2",
    ) -> str:
        assert self is not None
        return f"{p1}-{p2}"


__worker__ = TesterWorker()
