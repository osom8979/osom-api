# -*- coding: utf-8 -*-

from osom_api.aio.policy import RestoreEventLoopPolicy

# Restore uvloop's EventLoopPolicy to asyncio's DefaultEventLoopPolicy.
# This is being force-allocated within the aiogram library.
with RestoreEventLoopPolicy():
    from aiogram import (
        BaseMiddleware,
        Bot,
        Dispatcher,
        F,
        Router,
        __api_version__,
        __version__,
        enums,
        flags,
        html,
        md,
        methods,
        session,
        types,
    )

__all__ = (
    "BaseMiddleware",
    "Bot",
    "Dispatcher",
    "F",
    "Router",
    "__api_version__",
    "__version__",
    "enums",
    "flags",
    "html",
    "md",
    "methods",
    "session",
    "types",
)
