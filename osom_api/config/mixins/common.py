# -*- coding: utf-8 -*-


class CommonProps:
    command_prefix: str
    severity: str
    use_uvloop: bool
    debug: bool
    verbose: int

    def assert_common_properties(self) -> None:
        assert isinstance(self.command_prefix, str)
        assert isinstance(self.severity, str)
        assert isinstance(self.use_uvloop, bool)
        assert isinstance(self.debug, bool)
        assert isinstance(self.verbose, int)
