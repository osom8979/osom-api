# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Optional

from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_HTTP_TIMEOUT,
)
from osom_api.common.config import CommonConfig
from osom_api.random.hex import generate_hexdigits


class MasterConfig(CommonConfig):
    def __init__(
        self,
        http_host=DEFAULT_HTTP_HOST,
        http_port=DEFAULT_HTTP_PORT,
        http_timeout=DEFAULT_HTTP_TIMEOUT,
        api_token: Optional[str] = None,
        api_disable_auth=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.http_host = http_host
        self.http_port = http_port
        self.http_timeout = http_timeout

        self.api_token = api_token if api_token else generate_hexdigits(256)
        self.api_disable_auth = api_disable_auth

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.http_host, str)
        assert isinstance(args.http_port, int)
        assert isinstance(args.http_timeout, float)

        assert isinstance(args.api_token, (type(None), str))
        assert isinstance(args.api_disable_auth, bool)

        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))

    @property
    def loop_setup_type(self) -> LoopSetupType:
        return "uvloop" if self.use_uvloop else "asyncio"

    @property
    def opt_token(self) -> Optional[str]:
        return None if self.api_disable_auth else self.api_token
