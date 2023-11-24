# -*- coding: utf-8 -*-

from logging import Filter, LogRecord, getLogger
from typing import Final

from overrides import override

UVICORN_ACCESS_LOGGER_NAME: Final[str] = "uvicorn.access"


class HideHealthLogging(Filter):
    @override
    def filter(self, record: LogRecord) -> bool:
        if not record.args:
            return False

        if len(record.args) < 3:
            return False

        if not isinstance(record.args, tuple):
            return False

        return record.args[2] != "/health"


def hide_health_logging() -> None:
    getLogger(UVICORN_ACCESS_LOGGER_NAME).addFilter(HideHealthLogging())
