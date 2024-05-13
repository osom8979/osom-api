# -*- coding: utf-8 -*-

from osom_api.apps.worker.modules.common.worker import CommonWorker

__worker__ = CommonWorker()
__version__ = __worker__.version
__doc__ = __worker__.doc


async def on_async_open(*args, **kwargs) -> None:
    await __worker__.open(*args, **kwargs)


async def on_async_close() -> None:
    await __worker__.close()


async def on_run(data: bytes) -> bytes:
    return await __worker__.run(data)
