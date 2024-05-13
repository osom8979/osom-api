# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Optional

from osom_api.config import Config


class WorkerConfig(Config):
    def __init__(
        self,
        request_path: Optional[str] = None,
        module_path: Optional[str] = None,
        **kwargs,
    ):
        self.request_path = request_path
        self.module_path = module_path
        super().__init__(**kwargs)

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.request_path, (type(None), str))
        assert isinstance(args.module_path, (type(None), str))
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))
