# -*- coding: utf-8 -*-

from argparse import Namespace
from typing import Optional

# noinspection PyPackageRequirements
from uvicorn.config import LoopSetupType

from osom_api.arguments import (
    DEFAULT_API_OPENAPI_URL,
    DEFAULT_HTTP_HOST,
    DEFAULT_HTTP_PORT,
    DEFAULT_HTTP_TIMEOUT,
)
from osom_api.context.config import CommonConfig
from osom_api.random.hex import generate_hexdigits


class MasterConfig(CommonConfig):
    def __init__(
        self,
        http_host=DEFAULT_HTTP_HOST,
        http_port=DEFAULT_HTTP_PORT,
        http_timeout=DEFAULT_HTTP_TIMEOUT,
        api_token: Optional[str] = None,
        api_disable_auth=False,
        api_disable_docs=False,
        api_openapi_url=DEFAULT_API_OPENAPI_URL,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.http_host = http_host
        self.http_port = http_port
        self.http_timeout = http_timeout

        self.api_token = api_token if api_token else generate_hexdigits(256)
        self.api_disable_auth = api_disable_auth
        self.api_disable_docs = api_disable_docs
        self.api_openapi_url = api_openapi_url

    @classmethod
    def from_namespace(cls, args: Namespace):
        assert isinstance(args.http_host, str)
        assert isinstance(args.http_port, int)
        assert isinstance(args.http_timeout, float)

        assert isinstance(args.api_token, (type(None), str))
        assert isinstance(args.api_disable_auth, bool)
        assert isinstance(args.api_disable_docs, bool)
        assert isinstance(args.api_openapi_url, (type(None), str))

        cls.assert_common_properties(args)
        return cls(**cls.namespace_to_dict(args))

    @property
    def loop_setup_type(self) -> LoopSetupType:
        return "uvloop" if self.use_uvloop else "asyncio"

    @property
    def opt_api_token(self) -> Optional[str]:
        return None if self.api_disable_auth else self.api_token

    @property
    def opt_api_openapi_url(self) -> Optional[str]:
        return None if self.api_disable_docs else self.api_openapi_url
