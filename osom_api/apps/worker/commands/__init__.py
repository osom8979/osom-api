# -*- coding: utf-8 -*-

from typing import Dict

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.apps.worker.commands.progress.create import ProgressCreate
from osom_api.context import Context


def create_command_map(context: Context) -> Dict[str, WorkerCommand]:
    return {c.command: c for c in [ProgressCreate(context)]}
