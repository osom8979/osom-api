# -*- coding: utf-8 -*-

from enum import StrEnum, auto, unique
from inspect import iscoroutinefunction
from types import ModuleType
from typing import Sequence, Union

# noinspection PyProtectedMember
from plugpack.module.mixin._base import ModuleBase

from osom_api.context.msg import MsgRequest, MsgResponse
from osom_api.exceptions import (
    AlreadyInitializedError,
    NotACoroutineError,
    NotInitializedError,
)
from osom_api.worker.interface import CmdDesc, WorkerInterface


@unique
class ModuleKeys(StrEnum):
    worker = "__worker__"
    name = "__worker_name__"
    version = "__worker_version__"
    doc = "__worker_doc__"
    path = "__worker_path__"
    cmds = "__worker_cmds__"
    open = auto()
    close = auto()
    run = auto()


class Module(ModuleBase):
    def __init__(self, module: Union[str, ModuleType], isolate=False, *args, **kwargs):
        self._module = self.init_module(module, isolate)
        self._opened = False

        self.args = args
        self.kwargs = kwargs
        self.keys = ModuleKeys

        if self.has(self.keys.worker):
            worker = self.get(self.keys.worker)
            if not isinstance(worker, WorkerInterface):
                raise TypeError(f"Invalid worker type: {type(worker).__name__}")

            if not self.has(self.keys.name):
                self.set(self.keys.name, worker.name)
            if not self.has(self.keys.version):
                self.set(self.keys.version, worker.version)
            if not self.has(self.keys.doc):
                self.set(self.keys.doc, worker.doc)
            if not self.has(self.keys.path):
                self.set(self.keys.path, worker.path)
            if not self.has(self.keys.cmds):
                self.set(self.keys.cmds, worker.cmds)

            if not self.has(self.keys.open):
                self.set(self.keys.open, worker.open)
            if not self.has(self.keys.close):
                self.set(self.keys.close, worker.close)
            if not self.has(self.keys.run):
                self.set(self.keys.run, worker.run)

    @staticmethod
    def init_module(module: Union[str, ModuleType], isolate=False):
        if isinstance(module, str):
            return ModuleBase.import_module(module, isolate=isolate)
        else:
            return module

    @property
    def name(self) -> str:
        return self.opt(self.keys.name, str())

    @property
    def version(self) -> str:
        return self.opt(self.keys.version, str())

    @property
    def doc(self) -> str:
        return self.opt(self.keys.doc, str())

    @property
    def path(self) -> str:
        return self.opt(self.keys.path, str())

    @property
    def cmds(self) -> Sequence[CmdDesc]:
        return self.opt(self.keys.cmds, list())

    @property
    def has_open(self):
        return self.has(self.keys.open)

    @property
    def has_close(self):
        return self.has(self.keys.close)

    @property
    def has_run(self):
        return self.has(self.keys.run)

    @property
    def opened(self):
        return self._opened

    async def open(self, context) -> None:
        if self._opened:
            raise AlreadyInitializedError(
                f"The module has already been initialized: {self.module_name}"
            )

        callback = self.get(self.keys.open)

        if callback is not None and not iscoroutinefunction(callback):
            raise NotACoroutineError(
                f"Not a coroutine function: {self.module_name}.{self.keys.open}"
            )

        try:
            if callback is not None:
                await callback(context)
        except BaseException as e:
            raise RuntimeError(
                f"Raised a runtime error: {self.module_name}.{self.keys.open}"
            ) from e
        else:
            self._opened = True

    async def close(self) -> None:
        if not self._opened:
            raise NotInitializedError(
                f"The module is not initialized: {self.module_name}"
            )

        callback = self.get(self.keys.close)

        if callback is not None and not iscoroutinefunction(callback):
            raise NotACoroutineError(
                f"Not a coroutine function: {self.module_name}.{self.keys.close}"
            )

        try:
            if callback is not None:
                await callback()
        except BaseException as e:
            raise RuntimeError(
                f"Raised a runtime error: {self.module_name}.{self.keys.close}"
            ) from e
        finally:
            self._opened = False

    async def run(self, data: MsgRequest) -> MsgResponse:
        if not self._opened:
            raise NotInitializedError(
                f"The module is not initialized: {self.module_name}"
            )

        callback = self.get(self.keys.run)
        if callback is None:
            raise ValueError(
                f"The '{self.module_name}.{self.keys.run}' callback is required"
            )

        if not iscoroutinefunction(callback):
            raise NotACoroutineError(
                f"Not a coroutine function: {self.module_name}.{self.keys.run}"
            )

        try:
            result = await callback(data)
            if not isinstance(result, MsgResponse):
                raise TypeError(f"Invalid response type: {type(result).__name__}")
            return result
        except BaseException as e:
            raise RuntimeError(
                f"Raised a runtime error: {self.module_name}.{self.keys.run}"
            ) from e
