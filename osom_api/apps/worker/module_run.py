# -*- coding: utf-8 -*-

from typing import Any, Final

from plugpack.module.errors import ModuleCallbackRuntimeError

# noinspection PyProtectedMember
from plugpack.module.mixin._module_base import ModuleBase

ATTR_ON_RUN: Final[str] = "run"


class ModuleRun(ModuleBase):
    @property
    def has_on_run(self) -> bool:
        return self.has(ATTR_ON_RUN)

    async def on_run(self, data: Any) -> Any:
        try:
            return await self.get(ATTR_ON_RUN)(data)
        except BaseException as e:
            raise ModuleCallbackRuntimeError(self.name, ATTR_ON_RUN) from e
