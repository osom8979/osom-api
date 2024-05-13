# -*- coding: utf-8 -*-

from types import ModuleType
from typing import Any, Union

from plugpack.module.mixin.module_async_open import ModuleAsyncOpen
from plugpack.module.mixin.module_doc import ModuleDoc
from plugpack.module.mixin.module_version import ModuleVersion

from osom_api.apps.worker.module_run import ModuleRun


class Module(
    ModuleAsyncOpen,
    ModuleDoc,
    ModuleRun,
    ModuleVersion,
):
    def __init__(self, module: Union[str, ModuleType], isolate=False, *args, **kwargs):
        if isinstance(module, str):
            self._module = self.import_module(module, isolate=isolate)
        else:
            self._module = module
        self._args = args
        self._kwargs = kwargs

    async def async_open(self) -> None:
        await self.on_async_open(*self._args, **self._kwargs)

    async def async_close(self) -> None:
        await self.on_async_close()

    async def run(self, data: Any) -> Any:
        return await self.on_run(data)
