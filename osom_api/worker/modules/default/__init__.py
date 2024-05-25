# -*- coding: utf-8 -*-

from typing import Annotated

from osom_api.arguments import version as osom_version
from osom_api.worker.base import WorkerBase
from osom_api.worker.metas import ParamMeta


class DefaultWorker(WorkerBase):
    def __init__(self):
        super().__init__("default", osom_version(), "Default osom worker")
        self.register_command(self.on_chat)

    async def on_chat(
        self,
        n: Annotated[int, ParamMeta(doc="Number of chat completions", default=1)],
        model: Annotated[str, ParamMeta(doc="Chat model name", default="gpt-4o")],
    ) -> str:
        """Talk to the chatbot"""

        assert self is not None
        return f"{model}-{n}"


__worker__ = DefaultWorker()
