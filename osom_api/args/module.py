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

    @property
    def module_arguments(self) -> List[str]:
        if len(self.opts) >= 1 and self.opts[0] == "--":
            return self.opts[1:]
        else:
            return self.opts
