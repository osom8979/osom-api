# -*- coding: utf-8 -*-


class ModuleProps:
    module_path: str
    module_isolate: bool

    def assert_module_properties(self) -> None:
        assert isinstance(self.module_path, str)
        assert isinstance(self.module_isolate, bool)
