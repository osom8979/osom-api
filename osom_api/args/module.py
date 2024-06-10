# -*- coding: utf-8 -*-

from osom_api.args._common import CommonArgs, List


class ModuleArgs(CommonArgs):
    module_path: str
    module_isolate: bool
    opts: List[str]

    def assert_module_properties(self) -> None:
        assert isinstance(self.module_path, str)
        assert isinstance(self.module_isolate, bool)
        assert isinstance(self.opts, list)
