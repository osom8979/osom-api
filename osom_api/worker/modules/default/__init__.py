# -*- coding: utf-8 -*-

from osom_api.arguments import version as osom_version
from osom_api.worker.base import WorkerBase
from osom_api.worker.params import BodyParam


class DefaultWorker(WorkerBase):
    def __init__(self):
        super().__init__("default", osom_version(), "Default osom worker")
        self.register_command(self.on_echo)

    async def on_echo(self, message: BodyParam) -> str:
        """Echo the chat message"""
        assert self is not None
        return message


__worker__ = DefaultWorker()
