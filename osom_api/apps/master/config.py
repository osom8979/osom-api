# -*- coding: utf-8 -*-

from argparse import Namespace

from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_HTTP_TIMEOUT,
)
from osom_api.common.config import CommonConfig


class MasterConfig(CommonConfig):
    def __init__(
        self,
        http_host=DEFAULT_HTTP_HOST,
        http_port=DEFAULT_HTTP_PORT,
        http_timeout=DEFAULT_HTTP_TIMEOUT,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.http_host = http_host
        self.http_port = http_port
        self.http_timeout = http_timeout

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.http_host, str)
        assert isinstance(args.http_port, int)
        assert isinstance(args.http_timeout, float)
        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))

    @property
    def loop_setup_type(self) -> LoopSetupType:
        if self.use_uvloop:
            return "uvloop"
        else:
            return "asyncio"
