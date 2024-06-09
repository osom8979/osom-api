# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Any, Dict, List, Union

from type_serialize.inspect.member import get_public_instance_attributes

from osom_api.logging.logging import DEBUG, convert_level_number, logger


class BaseConfig(Namespace):
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
