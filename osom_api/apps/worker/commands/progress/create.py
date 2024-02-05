# -*- coding: utf-8 -*-

from typing import Any

from overrides import override

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.common.context import CommonContext


class ProgressCreate(WorkerCommand):
    __api__ = "/process/create"

    @override
    async def run(self, data: Any, context: CommonContext) -> Any:
        pass
