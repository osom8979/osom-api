# -*- coding: utf-8 -*-

from osom_api.args._common import CommonArgs


class ModuleArgs(CommonArgs):
    module_path: str
    module_isolate: bool

    def assert_module_properties(self) -> None:
        assert isinstance(self.module_path, str)
        assert isinstance(self.module_isolate, bool)
