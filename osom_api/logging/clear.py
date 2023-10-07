# -*- coding: utf-8 -*-

from logging import getLogger


def clear_root_handlers_in_realtime_logging() -> None:
    """
    Removes log handlers that were added inappropriately
    """
    try:
        import realtime.connection  # noqa
    except ImportError:
        pass
    else:
        getLogger().handlers.clear()
