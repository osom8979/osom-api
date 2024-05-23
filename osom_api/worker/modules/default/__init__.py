# -*- coding: utf-8 -*-

from typing import Annotated

from osom_api.arguments import version as osom_version
from osom_api.worker.base import ParamMeta, WorkerBase


class DefaultWorker(WorkerBase):
    def __init__(self):
        super().__init__("default", osom_version(), "Default osom worker")
        self.register_command(
            callback=self.on_chat,
            command="chat",
            summary="Talk to the chatbot",
        )

    async def on_chat(
        self,
        n: Annotated[int, ParamMeta(summary="Number of chat completions", default=1)],
        model: Annotated[str, ParamMeta(summary="Chat model name", default="gpt-4o")],
    ) -> str:
        assert self is not None
        return f"{model}-{n}"


__worker_context__ = DefaultWorker()
