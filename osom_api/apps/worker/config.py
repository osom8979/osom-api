# -*- coding: utf-8 -*-

from argparse import Namespace

from osom_api.config import Config


class WorkerConfig(Config):
    def __init__(self, request_key: str, **kwargs):
        self.request_key = request_key
        super().__init__(**kwargs)

    @classmethod
    def from_namespace(cls, args: Namespace):
        if not args.request_key:
            raise ValueError("Missing request key")
        assert isinstance(args.request_key, str)
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))
