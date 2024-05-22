# -*- coding: utf-8 -*-

from typing import Annotated, Optional

from osom_api.arguments import version as osom_version
from osom_api.worker.base import ParameterMeta, WorkerBase


class TesterWorker(WorkerBase):
    def __init__(self):
        super().__init__("test", osom_version(), "Test worker")
        self.register_command("cmd", "summary", self.on_cmd)

    async def on_cmd(
        self,
        p1: Annotated[int, ParameterMeta(summary="meta1", default=1)],
        p2: Annotated[str, ParameterMeta(summary="meta2", default="2")],
    ) -> str:
        assert self is not None
        return f"{p1}-{p2}"


__worker_context__ = TesterWorker()
