# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.config import Config


class WorkerConfig(Config):
    def __init__(
        self,
        module_path: str,
        isolate_module=False,
        **kwargs,
    ):
        self.module_path = module_path
        self.isolate_module = isolate_module
        super().__init__(**kwargs)

    @classmethod
    def from_namespace(cls, args: Namespace):
        if not args.module_path:
            raise ValueError("Missing module path")

        assert isinstance(args.module_path, str)
        assert isinstance(args.isolate_module, bool)

        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))
