# -*- coding: utf-8 -*-

from functools import lru_cache
from re import compile as re_compile
from typing import Dict

from osom_api.apps.worker.commands.interface import WorkerCommand
from osom_api.apps.worker.commands.progress.create import ProgressCreate
from osom_api.apps.worker.commands.progress.update import ProgressUpdate

COMMAND_API_REGEX = re_compile(r"([A-Z][0-9a-z]+)")


def get_command_api(cmd: WorkerCommand) -> str:
    return COMMAND_API_REGEX.sub(r"/\1", type(cmd).__name__).lower()


@lru_cache
def create_command_map() -> Dict[str, WorkerCommand]:
    return {get_command_api(c): c for c in [ProgressCreate(), ProgressUpdate()]}
