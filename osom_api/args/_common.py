# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Any, Dict, List, Union

from type_serialize.inspect.member import get_public_instance_attributes

from osom_api.logging.logging import DEBUG, convert_level_number, logger


class CommonArgs(Namespace):
    command_prefix: str
    severity: str
    use_uvloop: bool
    debug: bool
    verbose: int

    @staticmethod
    def namespace_to_dict(args: Namespace) -> Dict[str, Any]:
        return {k: v for k, v in get_public_instance_attributes(args)}

    def print(self, *args, **kwargs) -> Any:
        return getattr(self, "printer", print)(*args, **kwargs)

    def as_logging_lines(self) -> List[str]:
        result = list()
        for key, value in get_public_instance_attributes(self.args):
            name = key.replace("_", " ")
            name = name[0].upper() + name[1:]
            result.append(f"{name}: {value}")
        return result

    def logging_params(self, level: Union[str, int] = DEBUG) -> None:
        for line in self.as_logging_lines():
            logger.log(convert_level_number(level), line)

    def assert_common_properties(self) -> None:
        assert isinstance(self.command_prefix, str)
        assert isinstance(self.severity, str)
        assert isinstance(self.use_uvloop, bool)
        assert isinstance(self.debug, bool)
        assert isinstance(self.verbose, int)
