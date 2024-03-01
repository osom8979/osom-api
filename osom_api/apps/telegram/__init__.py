# -*- coding: utf-8 -*-

from osom_api.aio.policy import RestoreEventLoopPolicy

# Restore uvloop's EventLoopPolicy to asyncio's DefaultEventLoopPolicy.
# This is being force-allocated within the aiogram library.
with RestoreEventLoopPolicy():
    import aiogram  # noqa
